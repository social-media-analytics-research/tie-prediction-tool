from sklearn.metrics import roc_auc_score, roc_curve

from .metric import \
    EvaluationMetric


class ROC(EvaluationMetric):

    def __init__(self, y_true, y_score):
        super().__init__()
        fpr, tpr, _ = roc_curve(y_true, y_score)
        self.fpr = fpr
        self.tpr = tpr

    def get_json(self):
        json = {self.__class__.__name__: {"fpr": list(self.fpr), "tpr": list(self.tpr)}}
        return json


class AUC(EvaluationMetric):

    def __init__(self, y_true, y_score):
        super().__init__()
        auc = roc_auc_score(y_true, y_score)
        self.auc = auc

    def get_json(self):
        json = {self.__class__.__name__: self.auc}
        return json


def get_metrics_as_json(metrics):
    json = {}
    for metric in metrics:
        json[metric.__class__.__name__] = metric.get_json()[metric.__class__.__name__]
    return json
