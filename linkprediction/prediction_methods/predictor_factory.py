# Import classifiers
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

# Import similarity indices predictors
from linkprediction.prediction_methods.prediction.similarity_indices import (
    AdamicAdar, AdjustedRand, CommonNeighbors, Jaccard,
    Salton, PreferentialAttachement, Sorensen,
    ResourceAllocation, SameCommunity, ShortestPath,
    TotalNeighbors, UDegree, VDegree,
    HubPromoted, HubDepressed, LeichtHolmeNewman)

# Import social theory predictors
from linkprediction.prediction_methods.prediction.social_theory import (
    StructuralHoleTheory, SocialExchangeTheory,
    EndogenousBalanceTheory, EndogenousCollectiveActionTheory,
    HomophilyTheories, ResourceDependencyTheory,
    ExogenousBalanceTheory, ExogenousCollectiveActionTheory)


class LinkPredictorFactory:

    def create(self, model, **kwargs):
        if self._is_topology(model):
            return self._create_topology(model, **kwargs)
        elif self._is_socialtheory_endogenous(model):
            return self._create_socialtheory_endogenous(model, **kwargs)
        elif self._is_socialtheory_exogenous(model):
            return self._create_socialtheory_exogenous(model, **kwargs)
        elif self._is_classifier(model):
            return self._create_classifier(model, **kwargs)
        elif self._is_others(model):
            return self._create_others(model, **kwargs)
        else:
            raise ValueError(
                "Invalid value for `feature_type` ({0})."
                .format(model['feature_type'])
            )

    def _create_topology(self, model, graph):
        name = model['designation']

        if name == "AdamicAdar":
            return AdamicAdar(graph.to_undirected())
        elif name == "AdjustedRand":
            return AdjustedRand(graph.to_undirected())
        elif name == "CommonNeighbors":
            return CommonNeighbors(graph.to_undirected())
        elif name == "Jaccard":
            return Jaccard(graph.to_undirected())
        elif name == "Salton":
            return Salton(graph.to_undirected())
        elif name == "PreferentialAttachement":
            return PreferentialAttachement(graph.to_undirected())
        elif name == "ResourceAllocation":
            return ResourceAllocation(graph.to_undirected())
        elif name == "SameCommunity":
            return SameCommunity(graph.to_undirected())
        elif name == "ShortestPath":
            return ShortestPath(graph.to_undirected())
        elif name == "TotalNeighbors":
            return TotalNeighbors(graph.to_undirected())
        elif name == "UDegree":
            return UDegree(graph.to_undirected())
        elif name == "VDegree":
            return VDegree(graph.to_undirected())
        elif name == "Sorensen":
            return Sorensen(graph.to_undirected())
        elif name == "HubPromoted":
            return HubPromoted(graph.to_undirected())
        elif name == "HubDepressed":
            return HubDepressed(graph.to_undirected())
        elif name == "LeichtHolmeNewman":
            return LeichtHolmeNewman(graph.to_undirected())
        else:
            raise ValueError(
                "Invalid value for `designation` ({0})."
                .format(name)
            )

    def _create_socialtheory_endogenous(self, model, graph, predicted_graph, threshold):
        name = model['designation']

        if name == "SocialExchangeTheory":
            return SocialExchangeTheory(graph, predicted_graph)
        elif name == "BalanceTheory":
            return EndogenousBalanceTheory(graph, predicted_graph)
        elif name == "CollectiveActionTheory":
            return EndogenousCollectiveActionTheory(graph, predicted_graph)
        elif name == "StructuralHoleTheory":
            return StructuralHoleTheory(graph, predicted_graph)
        else:
            raise ValueError(
                "Invalid value for `designation` ({0})."
                .format(name)
            )

    def _create_socialtheory_exogenous(self, model, graph, predicted_graph, threshold):
        name = model['designation']
        weightings = {}
        for weight in model['parameters']['attribute_weightings']:
            weightings[weight['attribute']] = weight['value']

        if name == "HomophilyTheories":
            return HomophilyTheories(graph, predicted_graph, threshold, weightings)
        elif name == "BalanceTheory":
            return ExogenousBalanceTheory(graph, predicted_graph, threshold, weightings)
        elif name == "ResourceDependenceTheory":
            return ResourceDependencyTheory(graph, predicted_graph, threshold, weightings)
        elif name == "CollectiveActionTheory":
            return ExogenousCollectiveActionTheory(graph, predicted_graph, threshold, weightings)
        else:
            raise ValueError(
                "Invalid value for `designation` ({0})."
                .format(name)
            )

    def _create_classifier(self, model):
        name = model['designation']

        if name == "DecisionTree":
            return DecisionTreeClassifier()
        elif name == "SupportVector":
            return SVC(probability=True)
        elif name == "RandomForest":
            return RandomForestClassifier()
        elif name == "LogisticRegression":
            return LogisticRegression()
        elif name == "KNeighbors":
            return KNeighborsClassifier()
        elif name == "GaussianNB":
            return GaussianNB()
        elif name == "GradientBoosting":
            return GradientBoostingClassifier()
        else:
            raise ValueError(
                "Invalid value for `designation` ({0})."
                .format(name)
            )

    def _create_others(self, model):
        raise NotImplementedError()

    def _is_topology(self, model):
        return model['feature_type'] == 'Topology'

    def _is_socialtheory_endogenous(self, model):
        return model['feature_type'] == 'Social Theory with endogenous Attributes'

    def _is_socialtheory_exogenous(self, model):
        return model['feature_type'] == 'Social Theory with exogenous Attributes'

    def _is_classifier(self, model):
        return model['feature_type'] == 'ML-Classifier'

    def _is_others(self, model):
        return model['feature_type'] == 'Others'
