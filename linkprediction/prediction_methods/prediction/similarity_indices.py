from math import sqrt

from networkx import (
    Graph, adamic_adar_index, common_neighbors, jaccard_coefficient,
    preferential_attachment, resource_allocation_index, community,
    shortest_path_length)

from .predictor import \
    LinkPredictor


class AdamicAdar(LinkPredictor):

    def predict(self, node_pairs):
        predictions = adamic_adar_index(self.graph, node_pairs)
        return list(predictions)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'AdamicAdar'


class AdjustedRand(LinkPredictor):

    def predict(self, node_pairs):
        predictions = []
        for node_pair in node_pairs:
            uNeighborhood = self.graph.neighbors(node_pair[0])
            vNeighborhood = self.graph.neighbors(node_pair[1])
            uNeighborhood = list(uNeighborhood)
            vNeighborhood = list(vNeighborhood)
            intersectionNeighbors = list(common_neighbors(self.graph, node_pair[0], node_pair[1]))
            unionNeighbors = set().union(uNeighborhood, vNeighborhood)

            a = len(intersectionNeighbors)
            b = len(unionNeighbors)
            c = len(unionNeighbors)
            d = len(self.graph) - len(unionNeighbors)

            denominator = ((a+b) * (b+d)) + ((a+c) * (c+d))

            predictions.append((node_pair[0], node_pair[1], 2*(a*d - b*c) / denominator 
                               if denominator != 0 else 0))
        return predictions

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'AdjustedRand'


class CommonNeighbors(LinkPredictor):

    def predict(self, node_pairs):
        predictions = [(node_pair[0], node_pair[1], 
                       len(list(common_neighbors(self.graph, node_pair[0], node_pair[1]))))
                       for node_pair in node_pairs]
        return predictions

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'CommonNeighbors'


class Jaccard(LinkPredictor):

    def predict(self, node_pairs):
        predictions = jaccard_coefficient(self.graph, node_pairs)
        return list(predictions)

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'Jaccard'


class Salton(LinkPredictor):

    def predict(self, node_pairs):
        predictions = []
        for node_pair in node_pairs:
            uNeighborhood = self.graph.degree(node_pair[0])
            vNeighborhood = self.graph.degree(node_pair[1])
            intersection = common_neighbors(self.graph, node_pair[0], node_pair[1])
            intersection = len(list(intersection))
            denominator = sqrt(uNeighborhood * vNeighborhood)
            predictions.append((node_pair[0], node_pair[1], 
                               intersection / denominator if denominator != 0 else 0))
        return predictions

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'Salton'


class PreferentialAttachement(LinkPredictor):

    def predict(self, node_pairs):
        predictions = preferential_attachment(self.graph, node_pairs)
        return list(predictions)

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'PreferentialAttachement'


class ResourceAllocation(LinkPredictor):

    def predict(self, node_pairs):
        predictions = resource_allocation_index(self.graph, node_pairs)
        return list(predictions)

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'ResourceAllocation'


class SameCommunity(LinkPredictor):

    def __init__(self, graph, iterations: int = 1):
        super().__init__(graph)
        if iterations < 1:
            raise ValueError('Invalid iterations value. It must be greater '
                             'than or equal to 1!')
        self.iterations = iterations

    def predict(self, node_pairs):
        communities_generator = community.girvan_newman(self.graph)
        for i in range(self.iterations):
            level_communities = next(communities_generator)

        predictions = []
        for node_pair in node_pairs:
            uCommunityIndex = self._getCommunityIndex(node_pair[0], level_communities)
            vCommunityIndex = self._getCommunityIndex(node_pair[1], level_communities)
            predictions.append((node_pair[0], node_pair[1],
                               1 if (uCommunityIndex == vCommunityIndex and uCommunityIndex != -1) else 0))
        return predictions

    def _getCommunityIndex(self, node, communities):
        index = -1
        for community in communities:
            if node in community:
                index = communities.index(community)
        return index

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'SameCommunity'


class ShortestPath(LinkPredictor):

    def __init__(self, graph, method='dijkstra'):
        super().__init__(graph)
        self.method = method

    def predict(self, node_pairs):
        try:
            predictions = [(node_pair[0], node_pair[1],
                           shortest_path_length(self.graph, node_pair[0], node_pair[1], method=self.method))
                           for node_pair in node_pairs]
        except Exception:
            raise ValueError('Error during shortest path calculation. Probably'
                             ', the method does not exist!')
        return predictions

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'ShortestPath'


class TotalNeighbors(LinkPredictor):

    def predict(self, node_pairs):
        predictions = []
        for node_pair in node_pairs:
            uNeighborhood = self.graph.neighbors(node_pair[0])
            vNeighborhood = self.graph.neighbors(node_pair[1])
            uNeighborhood = list(uNeighborhood)
            vNeighborhood = list(vNeighborhood)
            predictions.append((node_pair[0], node_pair[1],
                               len(set().union(uNeighborhood, vNeighborhood))))
        return predictions

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'TotalNeighbors'


class UDegree(LinkPredictor):

    def predict(self, node_pairs):
        predictions = [(node_pair[0], node_pair[1], self.graph.degree(node_pair[0]))
                       for node_pair in node_pairs]
        return predictions

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'UDegree'


class VDegree(LinkPredictor):

    def predict(self, node_pairs):
        predictions = [(node_pair[0], node_pair[1], self.graph.degree(node_pair[1]))
                       for node_pair in node_pairs]
        return predictions

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'VDegree'


class Sorensen(LinkPredictor):

    def predict(self, node_pairs):
        predictions = []
        for node_pair in node_pairs:
            uNeighborhood = self.graph.degree(node_pair[0])
            vNeighborhood = self.graph.degree(node_pair[1])
            intersection = common_neighbors(self.graph, node_pair[0], node_pair[1])
            intersection = len(list(intersection))
            denominator = uNeighborhood + vNeighborhood
            predictions.append((node_pair[0], node_pair[1], 
                               2 * intersection / denominator if denominator != 0 else 0))
        return predictions

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'Sorensen'


class HubPromoted(LinkPredictor):

    def predict(self, node_pairs):
        predictions = []
        for node_pair in node_pairs:
            uNeighborhood = self.graph.degree(node_pair[0])
            vNeighborhood = self.graph.degree(node_pair[1])
            intersection = common_neighbors(self.graph, node_pair[0], node_pair[1])
            intersection = len(list(intersection))
            denominator = min(uNeighborhood, vNeighborhood)
            predictions.append((node_pair[0], node_pair[1], 
                               2 * intersection / denominator if denominator != 0 else 0))
        return predictions

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'HubPromoted'


class HubDepressed(LinkPredictor):

    def predict(self, node_pairs):
        predictions = []
        for node_pair in node_pairs:
            uNeighborhood = self.graph.degree(node_pair[0])
            vNeighborhood = self.graph.degree(node_pair[1])
            intersection = common_neighbors(self.graph, node_pair[0], node_pair[1])
            intersection = len(list(intersection))
            denominator = max(uNeighborhood, vNeighborhood)
            predictions.append((node_pair[0], node_pair[1], 
                               2 * intersection / denominator if denominator != 0 else 0))
        return predictions

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'HubDepressed'


class LeichtHolmeNewman(LinkPredictor):

    def predict(self, node_pairs):
        predictions = []
        for node_pair in node_pairs:
            uNeighborhood = self.graph.degree(node_pair[0])
            vNeighborhood = self.graph.degree(node_pair[1])
            intersection = common_neighbors(self.graph, node_pair[0], node_pair[1])
            intersection = len(list(intersection))
            denominator = uNeighborhood * vNeighborhood
            predictions.append((node_pair[0], node_pair[1], 
                               2 * intersection / denominator if denominator != 0 else 0))
        return predictions

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'LeichtHolmeNewman'
