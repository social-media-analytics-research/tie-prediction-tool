from collections import defaultdict
from operator import itemgetter

import numpy as np
import pandas as pd
import networkx as nx
from networkx.algorithms import community, structuralholes

from .predictor import \
    LinkPredictor

from linkprediction.database_connector import DatabaseConnector
from linkprediction.graph_import.predicted_graph_handler import \
    add_or_update_edge
from linkprediction.prediction_methods.prediction import (
    homophilies, triads)


# ******************************************* #
# * Theories based on endogenous Attributes * #
# ******************************************* #

# * 1. Endogenous Actor Level: Structural Hole Theory
class StructuralHoleTheory(LinkPredictor):

    def __init__(self, graph: nx.DiGraph, predicted_graph: nx.DiGraph, percentile_constraints=10):
        super().__init__(graph)
        self.predicted_graph = predicted_graph
        self.precentile_constraints = percentile_constraints

    def predict(self, node_pairs):
        # kernighan_lin_bisection: Nur für ungerichtete Graphen
        # K-Clique: Erfordert k (smallest community)
        # Fluid Communities: Anzahl der Comm erfordert
        # girvan_newman: Ist geeignet

        # Calculate constraints and replace nan values by 1
        constraints = structuralholes.constraint(self.graph)
        constraints_cleared = {key: (val if not np.isnan(val) else 1)
                               for key, val in constraints.items()}

        # Define all structural communities on the first level
        communities = next(community.girvan_newman(self.graph))

        # Define persons with lowest constraints for each community
        com_brokers = {}
        com_index = 0
        for com in communities:
            com_brokers[com_index] = []
            community_constraints = {
                val: constraints_cleared[val] for val in com}

            # Calculate nth-percentile to select nodes with lowest constraint
            nth_percentile_node_constraint = np.percentile(
                list(community_constraints.values()),
                self.precentile_constraints,
                axis=0,
                interpolation='nearest'
            )

            # Add persons with lowest constraints to com_brokers dict
            for node, constraint in community_constraints.items():
                if constraint <= nth_percentile_node_constraint:
                    com_brokers[com_index].append(node)
            com_index += 1

        # Define new constraints by combining top brokers from different communities
        # Create predicted edges that have lowest constraints
        for com_index, brokers in com_brokers.items():
            for broker in brokers:
                possible_counterparts = self._get_combinations(com_brokers, com_index)
                results = self._get_combination_results(self.graph, broker, possible_counterparts)
                if len(results) == 0:
                    continue
                chosen_counterpart = min(results, key=results.get)
                if results[chosen_counterpart] < constraints_cleared[broker]:
                    add_or_update_edge(
                        graph=self.predicted_graph,
                        edge=(broker, chosen_counterpart),
                        method_name='Endogenous Social Theory',
                        method_specified='StructuralHoleTheory',
                        score=1.0
                    )

    # * 1. Endogenous Actor Level: Structural Hole Theory - HelperMethods
    def _get_combinations(self, com_brokers, sel_com_index):
        possible_counterparts = []
        for com_index, brokers in com_brokers.items():
            if com_index == sel_com_index:
                continue
            for broker in brokers:
                possible_counterparts.append(broker)
        return possible_counterparts

    def _get_combination_results(self, graph, broker, possible_counterparts):
        combination_result = {}
        for counterpart in possible_counterparts:
            if graph.has_edge(broker, counterpart):
                continue
            graph.add_edge(broker, counterpart)
            if len(graph[broker]) != 0:
                constraint = sum(
                    structuralholes.local_constraint(graph, broker, n)
                    for n in set(nx.all_neighbors(graph, broker))
                )
            else:
                # Constraint is not defined for isolated nodes
                constraint = 1
            combination_result[counterpart] = constraint
            graph.remove_edge(broker, counterpart)
        return combination_result

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'StructuralHoleTheory'


# * 2. Endogenous Dyadic Level: Social Exchange Theory
class SocialExchangeTheory(LinkPredictor):

    def __init__(self, graph: nx.DiGraph, predicted_graph: nx.DiGraph):
        super().__init__(graph)
        self.predicted_graph = predicted_graph

    def predict(self, node_pairs):
        for edge in self.graph.edges:
            reverse_edge = (edge[1], edge[0])
            if not self.graph.has_edge(*reverse_edge):
                add_or_update_edge(
                    self.predicted_graph,
                    reverse_edge,
                    'Endogenous Social Theory',
                    'SocialExchangeTheory',
                    1.0
                )

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'SocialExchangeTheory'


# * 3. Endogenous Triadic Level: Balance Theory
class EndogenousBalanceTheory(LinkPredictor):

    def __init__(self, graph: nx.DiGraph, predicted_graph: nx.DiGraph):
        super().__init__(graph)
        self.predicted_graph = predicted_graph

    def predict(self, node_pairs):
        balance_theory_triads = triads.triadic_enumeration(
            self.graph,
            set(['021C', '111D', '111U', '030C', '201', '120C', '210'])
        )
        assesed_triads = set()
        for triad_type, triad_list in balance_theory_triads.items():
            for current_triad in triad_list:
                current_triad_sorted = tuple(sorted(current_triad))
                if current_triad_sorted not in assesed_triads:
                    assesed_triads.add(current_triad_sorted)
                    edges = triads.get_missing_edges_for_bt(
                        self.graph.subgraph(current_triad)
                        )
                    for edge in edges:
                        add_or_update_edge(
                            self.predicted_graph,
                            edge,
                            'Endogenous Social Theory',
                            f'BalanceTheory.{triad_type}',
                            1.0
                        )

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'BalanceTheory'


# * 4. Endogenous Global Level: Collective Action Theory
class EndogenousCollectiveActionTheory(LinkPredictor):

    def __init__(self, graph: nx.DiGraph, predicted_graph: nx.DiGraph, max_distance=3, percentile_centrality=80, precentile_distant_nodes=90):
        super().__init__(graph)
        self.predicted_graph = predicted_graph
        self.max_distance = max_distance
        self.precentile_centrality = percentile_centrality
        self.precentile_distant_nodes = precentile_distant_nodes

    def predict(self, node_pairs):
        # Calculate katz centrality for every node
        # katz_centrality gives errors sometimes
        # centrality = nx.katz_centrality(original_graph)
        centrality = nx.katz_centrality_numpy(self.graph)

        # Order nodes by centrality
        centrality_ordered = {k: v for k, v in sorted(
            centrality.items(), key=itemgetter(1)
        )}

        # Calculate n-th percentile of centrality values
        nth_percentile_centrality = np.percentile(
            list(centrality_ordered.values()), self.precentile_centrality, axis=0, interpolation='nearest'
        )

        # Retrieve all k, v pairs that are equal or bigger to percentile
        most_central_nodes = {
            k: v for k, v in centrality_ordered.items() if v >= nth_percentile_centrality
        }

        # Calculate shortest paths between nodes
        undirected_graph = self.graph.to_undirected(as_view=True)
        for central_node, centrality in most_central_nodes.items():
            shortest_paths = nx.single_source_shortest_path_length(
                undirected_graph, central_node
            )
            # Remove paths with length 0 or 1
            for destination, length in list(shortest_paths.items()):
                if length <= 1 or length > self.max_distance:
                    del shortest_paths[destination]
            if len(shortest_paths) == 0:
                continue
            distant_nodes = {
                key: centrality_ordered[key] for key in shortest_paths.keys()
            }
            distant_nodes_ordered = {
                k: v for k, v in sorted(distant_nodes.items(), key=itemgetter(1))
            }
            # Calculate nth-percentile to select nodes with highest centrality
            nth_percentile_distant_nodes = np.percentile(
                list(distant_nodes_ordered.values()),
                self.precentile_distant_nodes,
                axis=0,
                interpolation='nearest'
            )
            for distant_node, centrality in distant_nodes_ordered.items():
                if centrality >= nth_percentile_distant_nodes:
                    add_or_update_edge(
                        self.predicted_graph,
                        (central_node, distant_node),
                        'Endogenous Social Theory',
                        'CollectiveActionTheory',
                        1.0
                    )

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'CollectiveActionTheory'


# ****************************************** #
# * Theories based on exogenous Attributes * #
# ****************************************** #

ATTR_HANDLING = {
    'occupation': homophilies.occupation_similarity,
    'level_of_education': homophilies.level_of_education_similarity,
    'gender': homophilies.default,
    'institution': homophilies.default,
    'type_of_education': homophilies.default,
    'primary_location': homophilies.default,
    'digital_affinity': None,
    'label': None,
}


def get_attribute_threshold(graph: nx.DiGraph, weightings: dict):
    """
    1. Jede vorhandene Kante iterieren
    2. Für jedes gemeinsame Attribut einer Kante die Ähnlichkeit zwischen 0-1 ermitteln (0=grundlegend verschieden, 1=identisch)
    3. Für jedes Attribut einen Zähler hochzählen (da es Knoten ohne bestimmte Attribute geben könnte)
    4. Für jedes Attribut die Ähnlichkeiten abspeichern (aufaddieren?)
    5. Summe / Zähler pro Attribut
    6. Gesamtdurchschnitt ermitteln
    """
    edge_counter = 0
    attr_similarities = 0
    if graph.number_of_edges() == 0 or graph.number_of_nodes() == 0:
        # Return default value
        return 0.5
    for edge in graph.edges:
        u = graph.nodes[edge[0]]
        v = graph.nodes[edge[1]]
        similarity = _get_similarity(u, v, weightings)
        if similarity is None:
            continue
        edge_counter += 1
        attr_similarities += similarity
    if edge_counter == 0:
        # Return default value
        return 0.5
    return attr_similarities / edge_counter


def _get_similarity(u, v, weightings: dict):
    # ? Similarities zwischenspeichern?
    """
    u: source node
    v: target node
    weightings: dict containing all attributes:
        key: attribute_name, value: weight
    """
    attr_counter = 0
    attr_similarities = 0
    for attr in u:
        # Both attribute lists must have the same attribute
        # The attribute mustn't be empty
        if attr not in v or not v[attr] \
                or attr not in ATTR_HANDLING or ATTR_HANDLING[attr] is None:
            continue
        attr_counter += 1
        attr_similarity_uniformed = ATTR_HANDLING.get(
            attr, homophilies.default
        )(u[attr], v[attr])
        if attr in weightings:
            attr_similarities += weightings[attr] * attr_similarity_uniformed
        else:
            attr_similarities += attr_similarity_uniformed
    if attr_counter == 0:
        return None
    return attr_similarities / attr_counter


# * 5. Exogenous Attribute Actor Level: Homophily Theories
class HomophilyTheories(LinkPredictor):

    def __init__(self, graph: nx.DiGraph, predicted_graph: nx.DiGraph, threshold: float, weightings: dict):
        super().__init__(graph)
        self.predicted_graph = predicted_graph
        self.threshold = threshold
        self.weightings = weightings

    def predict(self, node_pairs):
        """
        Resource Dependence Theory automatically applied.
        """
        for u in self.graph.nodes:
            for v in self.graph.nodes:
                if u == v or self.graph.has_edge(u, v):
                    continue
                u_node = self.graph.nodes[u]
                v_node = self.graph.nodes[v]
                if _get_similarity(u_node, v_node, self.weightings) > self.threshold:
                    add_or_update_edge(
                        graph=self.predicted_graph,
                        edge=(u, v),
                        method_name='Exogenous Social Theory',
                        method_specified='HomophilyTheories',
                        score=1.0
                    )

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'HomophilyTheories'


# * 6. Exogenous Attribute Dyadic Level: Resource Dependence Theory
class ResourceDependencyTheory(LinkPredictor):

    def __init__(self, graph: nx.DiGraph, predicted_graph: nx.DiGraph, threshold: float, weightings: dict):
        super().__init__(graph)
        self.predicted_graph = predicted_graph
        self.threshold = threshold
        self.weightings = weightings

    def predict(self, node_pairs):
        for edge in self.graph.edges:
            reverse_edge = (edge[1], edge[0])
            u_node = self.graph.nodes[edge[1]]
            v_node = self.graph.nodes[edge[0]]
            if not self.graph.has_edge(*reverse_edge) and \
                    _get_similarity(u_node, v_node, self.weightings) > self.threshold:
                add_or_update_edge(
                    self.predicted_graph,
                    reverse_edge,
                    'Exogenous Social Theory',
                    'ResourceDependenceTheory',
                    1.0
                )

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'ResourceDependenceTheory'


# * 7. Endogenous Triadic Level: Balance Theory
class ExogenousBalanceTheory(LinkPredictor):

    def __init__(self, graph: nx.DiGraph, predicted_graph: nx.DiGraph, threshold: float, weightings: dict):
        super().__init__(graph)
        self.predicted_graph = predicted_graph
        self.threshold = threshold
        self.weightings = weightings

    def predict(self, node_pairs):
        balance_theory_triads = triads.triadic_enumeration(
            self.graph,
            set(['021C', '111D', '111U', '030C', '201', '120C', '210'])
        )
        assesed_triads = set()
        for triad_type, triad_list in balance_theory_triads.items():
            for current_triad in triad_list:
                current_triad_sorted = tuple(sorted(current_triad))
                if current_triad_sorted not in assesed_triads:
                    assesed_triads.add(current_triad_sorted)
                    u = self.graph.nodes[current_triad_sorted[0]]
                    v = self.graph.nodes[current_triad_sorted[1]]
                    w = self.graph.nodes[current_triad_sorted[2]]
                    if not _get_similarity(u, v, self.weightings) > self.threshold \
                        or not _get_similarity(v, w, self.weightings) > self.threshold \
                            or not _get_similarity(u, w, self.weightings) > self.threshold:
                        continue
                    edges = triads.get_missing_edges_for_bt(
                        self.graph.subgraph(current_triad)
                    )
                    for edge in edges:
                        add_or_update_edge(
                            self.predicted_graph,
                            edge,
                            'Exogenous Social Theory',
                            f'BalanceTheory.{triad_type}',
                            1.0
                        )

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'BalanceTheory'


# * 8. Endogenous Global Level: Collective Action Theory
class ExogenousCollectiveActionTheory(LinkPredictor):

    def __init__(self, graph: nx.DiGraph, predicted_graph: nx.DiGraph, threshold: float, weightings: dict, max_distance=3, percentile_centrality=80, precentile_distant_nodes=90):
        super().__init__(graph)
        self.predicted_graph = predicted_graph
        self.threshold = threshold
        self.weightings = weightings
        self.max_distance = max_distance
        self.precentile_centrality = percentile_centrality
        self.precentile_distant_nodes = precentile_distant_nodes

    def predict(self, node_pairs):
        node_centralities = {}
        graph_centralities = {}
        subgraphs = {}
        for u in self.graph.nodes:
            u_node = self.graph.nodes[u]
            subgraphs[u] = self.graph.copy()
            for v in self.graph.nodes:
                v_node = self.graph.nodes[v]
                if u == v:
                    continue
                if _get_similarity(u_node, v_node, self.weightings) <= self.threshold:
                    subgraphs[u].remove_node(v)
            # Calculate katz centrality for u
            # Order nodes by centrality
            local_centrality_ordered = {k: v for k, v in sorted(
                nx.katz_centrality(subgraphs[u]).items(),
                key=itemgetter(1)
            )}
            graph_centralities[u] = local_centrality_ordered
            node_centralities[u] = local_centrality_ordered[u]

        # Order nodes by centrality
        global_centrality_ordered = {k: v for k, v in sorted(
            node_centralities.items(), key=itemgetter(1)
        )}

        # Calculate n-th percentile of centrality values
        nth_percentile_centrality = np.percentile(
            list(global_centrality_ordered.values()),
            self.precentile_centrality,
            axis=0,
            interpolation='nearest'
        )

        # Retrieve all k, v pairs that are equal or bigger to percentile
        most_central_nodes = {
            k: v for k, v in global_centrality_ordered.items() if v >= nth_percentile_centrality
        }

        # Calculate shortest paths between nodes
        for central_node, centrality in most_central_nodes.items():
            shortest_paths = nx.single_source_shortest_path_length(
                subgraphs[central_node].to_undirected(as_view=True),
                central_node
            )
            # Remove paths with length 0 or 1
            for destination, length in list(shortest_paths.items()):
                if length <= 1 or length > self.max_distance:
                    del shortest_paths[destination]
            if len(shortest_paths) == 0:
                continue
            distant_nodes = {
                key: graph_centralities[central_node][key] for key in shortest_paths.keys()
            }
            distant_nodes_ordered = {
                k: v for k, v in sorted(distant_nodes.items(), key=itemgetter(1))
            }
            # Calculate nth-percentile to select nodes with highest centrality
            nth_percentile_distant_nodes = np.percentile(
                list(distant_nodes_ordered.values()),
                self.precentile_distant_nodes,
                axis=0,
                interpolation='nearest'
            )
            for distant_node, centrality in distant_nodes_ordered.items():
                if centrality >= nth_percentile_distant_nodes:
                    add_or_update_edge(
                        self.predicted_graph,
                        (central_node, distant_node),
                        'Exogenous Social Theory',
                        'CollectiveActionTheory',
                        1.0
                    )

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'CollectiveActionTheory'
