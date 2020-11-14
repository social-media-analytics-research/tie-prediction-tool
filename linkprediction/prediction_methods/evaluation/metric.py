from abc import ABC, abstractmethod


class EvaluationMetric(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_json(self):
        pass
