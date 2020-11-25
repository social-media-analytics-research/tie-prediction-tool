from .predictor import LinkPredictor


class UAttribute(LinkPredictor):

    def __init__(self, graph, attribute):
        super().__init__(graph)
        self.attribute = attribute

    def predict(self, node_pairs):
        try:
            attributes = [(node_pair[0], node_pair[1], self.graph.nodes[node_pairs[0]][self.attribute])
                          for node_pair in node_pairs]
        except Exception:
            raise ValueError('Invalid node attribute value. '
                             'It must be defined in the graph!')
        return attributes

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'UAttribute'


class VAttribute(LinkPredictor):

    def __init__(self, graph, attribute):
        super().__init__(graph)
        self.attribute = attribute

    def predict(self, node_pairs):
        try:
            attributes = [(node_pair[0], node_pair[1], self.graph.nodes[node_pairs[1]][self.attribute])
                          for node_pair in node_pairs]
        except Exception:
            raise ValueError('Invalid node attribute value. '
                             'It must be defined in the graph!')
        return attributes

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return 'VAttribute'
