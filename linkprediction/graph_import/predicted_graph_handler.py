from collections import defaultdict

import networkx as nx
from networkx import DiGraph
from pandas import DataFrame

from linkprediction.database_connector import DatabaseConnector

COLOR_PREDICTED_ONLY = '#EB5F5E'
COLOR_MIXED = '#F3A533'


# * Method to add edge to graph
def add_or_update_edge(
    graph: nx.DiGraph,
    edge: tuple,
    method_name: str,
    method_specified: str,
    score: float
):
    edge_exists = graph.has_edge(*edge)
    edge_rev_exists = graph.has_edge(edge[1], edge[0])
    if not edge_exists and not edge_rev_exists:
        id0 = graph.nodes[edge[0]]['identifiers']['node_network_id']
        id1 = graph.nodes[edge[1]]['identifiers']['node_network_id']
        graph.add_edge(
            *edge,
            edges=[{
                'source': edge[0],
                'target': edge[1],
                'predicted': True,
                'prediction_score':score,
                'applied_methods': {method_name: [method_specified]}
            }],
            edge_color=COLOR_PREDICTED_ONLY,
            identifiers={
                id0: graph.nodes[edge[0]]['identifiers']['node_id'],
                id1: graph.nodes[edge[1]]['identifiers']['node_id'],
                'original_network_id': graph.nodes[edge[0]]['identifiers']['original_network_id'],
                'predicted_network_id': graph.nodes[edge[0]]['identifiers']['predicted_network_id']
            }
        )
    else:
        actual_edge = edge if edge_exists else (edge[1], edge[0])
        single_edges = graph.get_edge_data(*actual_edge)
        add_edge = True
        reverse_edge_predicted = False
        for single_edge in single_edges['edges']:
            if single_edge['source'] == edge[0] and single_edge['target'] == edge[1]:
                if single_edge['predicted'] is True:
                    single_edge['prediction_score'] += score
                    if method_name in single_edge['applied_methods']:
                        single_edge['applied_methods'][method_name].append(method_specified)
                    else:
                        single_edge['applied_methods'][method_name] = [method_specified]
                add_edge = False
            if single_edge['source'] == edge[1] and single_edge['target'] == edge[0] \
                    and single_edge['predicted'] is True:
                reverse_edge_predicted = True
        if add_edge is True:
            single_edges['edges'].append({
                'source': edge[0],
                'target': edge[1],
                'predicted': True,
                'prediction_score': score,
                'applied_methods': {method_name: [method_specified]}
            })
            if reverse_edge_predicted is False:
                single_edges['edge_color'] = COLOR_MIXED


def load_predicted_graph_from_db(predicted_network_id: str):
    db = DatabaseConnector()
    nodes = db.get_nodes_by_id('predicted_network_id', predicted_network_id)
    uuid_to_id = {node['node_id']: node['node_network_id'] for node in nodes}
    dict_nodes = []
    for node in nodes:
        dict_nodes.append({'id': node['node_network_id']})

    directed_edge_count = 0
    undirected_edge_count = 0

    dict_edges = []
    edges = db.get_edges_of_predicted_network_by_id('predicted_network_id', predicted_network_id)
    methods_applied = dict(defaultdict(int))
    for edge in edges:
        edge_comps = db.get_components_of_predicted_edge_by_id(
            'predicted_edge_id',
            edge['predicted_edge_id']
        )
        directed_edge_count += len(edge_comps)
        undirected_edge_count += 1

        edge_draft = {
            'source': uuid_to_id[edge['source_node']],
            'target': uuid_to_id[edge['target_node']],
            'edge_color': edge['edge_color'],
            'edges': []
        }

        for edge_comp in edge_comps:
            sub_edge = {
                'source': uuid_to_id[edge_comp['source']],
                'target': uuid_to_id[edge_comp['target']],
                'predicted': edge_comp['predicted']
            }
            if sub_edge['predicted'] is True:
                sub_edge['prediction_score'] = edge_comp['prediction_score']
                methods = db.get_applied_methods_of_predicted_edge_component_by_id(
                    'edge_component_id',
                    edge_comp['edge_component_id']
                )
                sub_edge['applied_methods'] = {}
                for method in methods:
                    sub_edge['applied_methods'][
                        method['method_designation']
                    ] = method['method_components']
                    if method['method_designation'] not in methods_applied:
                        methods_applied[method['method_designation']] = {}
                    for spec_method in method['method_components']:
                        if spec_method not in methods_applied[method['method_designation']]:
                            methods_applied[method['method_designation']][spec_method] = 1
                        else:
                            methods_applied[method['method_designation']][spec_method] += 1
            else:
                sub_edge['prediction_score'] = 1

            edge_draft['edges'].append(sub_edge)
        dict_edges.append(edge_draft)
    return {
        'nodes': dict_nodes,
        'links': dict_edges,
        'information': {
            'node_count': len(nodes),
            'directed_edge_count': directed_edge_count,
            'undirected_edge_count': undirected_edge_count,
            'methods_applied': methods_applied
        }
    }


def save_predicted_graph_to_db(predicted_graph: DiGraph, predicted_network_id: str):
    db = DatabaseConnector()
    db.delete_edges_of_predicted_network_by_id('predicted_network_id', predicted_network_id)
    for edge in predicted_graph.edges:
        edge_data = predicted_graph[edge[0]][edge[1]]
        if 'edges' not in edge_data:
            continue
        edge = (
            edge_data['identifiers'][edge[0]],
            edge_data['identifiers'][edge[1]]
        )
        edge_color = edge_data['edge_color']
        edge_id = db.add_edge_to_predicted_network(edge, edge_color, predicted_network_id)

        for edge_comp in edge_data['edges']:
            sub_edge = (
                edge_data['identifiers'][edge_comp['source']],
                edge_data['identifiers'][edge_comp['target']]
            )
            if 'prediction_score' not in edge_comp:
                edge_comp['prediction_score'] = None
            edge_comp_id = db.add_component_to_predicted_edge(
                sub_edge,
                edge_comp['predicted'],
                edge_comp['prediction_score'],
                edge_id
            )
            if 'applied_methods' not in edge_comp:
                continue
            applied_methods = []
            for method in edge_comp['applied_methods']:
                applied_methods.append((method, edge_comp['applied_methods'][method]))
            db.add_applied_methods_to_predicted_edge_component(
                applied_methods,
                edge_comp_id
            )


def get_st_features_from_predicted_graph(predicted_graph: DiGraph, node_pairs: list):
    df = DataFrame({'node_pairs': node_pairs})
    for edge in predicted_graph.edges:
        edge_data = predicted_graph[edge[0]][edge[1]]
        if 'edges' not in edge_data:
            continue
        for edge_comp in edge_data['edges']:
            if edge_comp['predicted'] is False or 'applied_methods' not in edge_comp:
                continue
            node_pair = df.loc[df['node_pairs'] == (edge_comp['source'], edge_comp['target'])]
            if node_pair.empty is True:
                continue
            applied_methods = []
            for method_category in edge_comp['applied_methods']:
                for method in edge_comp['applied_methods'][method_category]:
                    if method not in df.columns:
                        df[method] = 0
                    df_index_filter = df['node_pairs'] == (edge_comp['source'], edge_comp['target'])
                    df.loc[df_index_filter, method] = 1
    return df


def hierarchical_to_flat(h_graph: DiGraph):
    f_graph = h_graph.copy()
    for edge in f_graph.edges:
        edge_data = f_graph[edge[0]][edge[1]]
        if 'edges' not in edge_data:
            continue
        if 'source_node' not in edge_data['identifiers'] and \
                edge[0] in edge_data['identifiers']:
            edge_data['identifiers']['source_node'] = edge_data['identifiers'][edge[0]]
        if 'target_node' not in edge_data['identifiers'] and \
                edge[1] in edge_data['identifiers']:
            edge_data['identifiers']['target_node'] = edge_data['identifiers'][edge[1]]

        for edge_comp in edge_data['edges']:
            if edge[0] == edge_comp['source'] and \
                    edge[1] == edge_comp['target']:
                edge_data['predicted'] = edge_comp['predicted']
                if edge_comp['predicted'] is True:
                    edge_data['prediction_score'] = edge_comp['prediction_score']
                    edge_data['applied_methods'] = edge_comp['applied_methods']
                else:
                    edge_data['prediction_score'] = None
                    edge_data['applied_methods'] = None
                continue

            applied_methods = None
            if edge_comp['predicted']:
                applied_methods = edge_comp['applied_methods']

            if 'prediction_score' not in edge_comp:
                edge_comp['prediction_score'] = None

            f_graph.add_edge(
                edge_comp['source'], edge_comp['target'],
                predicted=edge_comp['predicted'],
                edge_color=edge_data['edge_color'],
                prediction_score=edge_comp['prediction_score'],
                applied_methods=applied_methods,
                identifiers={
                    'source_node': edge_data['identifiers']['target_node'],
                    'target_node': edge_data['identifiers']['source_node'],
                    'original_network_id': edge_data['identifiers']['original_network_id'],
                    edge_comp['source']: edge_data['identifiers']['target_node'],
                    edge_comp['target']: edge_data['identifiers']['source_node']
                }
            )
        del edge_data['edges']
    return f_graph


def flat_to_hierarchical(f_graph: DiGraph):
    h_graph = f_graph.copy()
    for edge in h_graph.edges:
        edge_data = h_graph[edge[0]][edge[1]]
        if 'edges' not in edge_data:
            edge_data['edges'] = []
        sub_edge = {
            'source': edge[0],
            'target': edge[1],
            'predicted': edge_data['predicted']
        }
        if edge_data['predicted'] is True:
            sub_edge['prediction_score'] = edge_data['prediction_score']
            sub_edge['applied_methods'] = edge_data['applied_methods']
        edge_data['edges'].append(sub_edge)

        if h_graph.has_edge(edge[1], edge[0]):
            sub_edge_data = h_graph[edge[1]][edge[0]]
            sub_edge = {
                'source': edge[1],
                'target': edge[0],
                'predicted': sub_edge_data['predicted']
            }
            if sub_edge_data['predicted'] is True:
                sub_edge['prediction_score'] = sub_edge_data['prediction_score']
                sub_edge['applied_methods'] = sub_edge_data['applied_methods']
            edge_data['edges'].append(sub_edge)
            h_graph.remove_edge(edge[1], edge[0])
        if edge_data['predicted'] is True:
            del edge_data['prediction_score']
            del edge_data['applied_methods']
        del edge_data['predicted']
    return h_graph
