from abc import ABC, abstractmethod
from networkx import Graph


class LinkPredictor(ABC):

    def __init__(self, graph: Graph):
        super().__init__()
        self.graph = graph

    @abstractmethod
    def predict(self, node_pairs):
        pass
