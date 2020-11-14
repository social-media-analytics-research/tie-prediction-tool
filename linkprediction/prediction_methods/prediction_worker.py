import os
import sys
from collections import Counter
from functools import partial
import datetime

import networkx as nx
import numpy as np
import pandas as pd
from numba import jit

from sklearn.metrics import roc_auc_score, roc_curve

from linkprediction.database_connector import DatabaseConnector
from linkprediction.graph_import.original_graph_handler import \
    build_original_graph
from linkprediction.graph_import.predicted_graph_handler import \
    load_predicted_graph_from_db
from linkprediction.prediction_methods.preparation.preprocessing import \
    preprocess_df
from linkprediction.prediction_methods.preparation.utility import \
    assign_labels
from linkprediction.prediction_methods.preparation.sampling import (
    find_all_missing_edges, sampling_by_percentage)
from linkprediction.prediction_methods.prediction.utility import (
    get_prediction, get_dataframe)
from linkprediction.prediction_methods.prediction.classification import (
    get_X_y)
from linkprediction.prediction_methods.predictor_factory import \
    LinkPredictorFactory
from linkprediction.prediction_methods.prediction_monitor import \
    PredictionMonitor
from linkprediction.prediction_methods.prediction.social_theory import \
    get_attribute_threshold
from linkprediction.prediction_methods.evaluation.metrics import (
    ROC, AUC, get_metrics_as_json)
from linkprediction.graph_import.predicted_graph_handler import (
    save_predicted_graph_to_db, get_st_features_from_predicted_graph, 
    add_or_update_edge, hierarchical_to_flat, flat_to_hierarchical)


class PredictionWorker(object):

    def __init__(self,
                 process_id,
                 project_id,
                 predictors,
                 validation,
                 preprocessing,
                 train_split,
                 test_split,
                 seed):
        self.process_id = process_id
        self.project_id = project_id
        self.predictors = predictors
        self.validation = validation
        self.preprocessing = preprocessing
        self.train_split = train_split
        self.test_split = test_split
        self.seed = seed
        self.monitor = PredictionMonitor(self, self._get_tasks())
        self.factory = LinkPredictorFactory()

    def predict(self):
        try:
            self.monitor.pending()

            # PIPELINE - PREPARATION
            ground_truth_graph_h = build_original_graph('project_id', self.project_id, 'hierarchical')
            ground_truth_graph_f = hierarchical_to_flat(ground_truth_graph_h)
            train_graph_f, test_graph_f = self._sample_graphs(ground_truth_graph_f)
            train_missing_edges, test_missing_edges = self._get_missing_edges(ground_truth_graph_f, train_graph_f, test_graph_f)
            train_set, test_set = self._prepare_labels(ground_truth_graph_f, test_graph_f, train_missing_edges, test_missing_edges)

            train_graph_h = flat_to_hierarchical(train_graph_f)
            predicted_graph_train = train_graph_h.copy()
            test_graph_h = None
            predicted_graph_test = None
            if self.validation:
                test_graph_h = flat_to_hierarchical(test_graph_f)
                predicted_graph_test = test_graph_h.copy()

            # PIPELINE - TOPOLOGY
            train_t_df, test_t_df = self._topology_pipeline(ground_truth_graph_f, train_graph_f, test_graph_f, train_set, test_set)     

            # PIPELINE - SOCIALTHEORY
            train_st_df, test_st_df = self._socialtheory_pipeline(train_graph_h, test_graph_h, train_set, test_set, predicted_graph_train, predicted_graph_test)

            # PIPELINE - CLASSIFICATION
            train_features_df = pd.concat([train_t_df, train_st_df], axis=1)
            test_features_df = None
            if not test_t_df is None:
                test_features_df = pd.concat([test_t_df, test_st_df], axis=1)

            train_c_df, test_c_df = self._classification_pipeline(train_features_df, test_features_df)

            # CREATE PREDICTED GRAPH
            self._add_topology_to_predicted_graph(train_t_df, test_t_df, predicted_graph_train, predicted_graph_test)
            self._add_classification_to_predicted_graph(train_set.node_pairs, train_c_df, test_c_df, predicted_graph_train, predicted_graph_test)
            train_final = pd.concat([train_set.node_pairs, train_c_df], axis=1)
            train_final = pd.concat([train_set.label, train_final], axis=1)

            test_final = None
            if not test_c_df is None:
                test_final = pd.concat([test_set.node_pairs, test_c_df], axis=1)
                test_final = pd.concat([test_set.label, test_final], axis=1)

            self._save_predicted_graph(predicted_graph_train, predicted_graph_test)

            # PIPELINE - EVALUATION
            results_train, results_test = self._create_results(
                train_final, test_final)

            db_instance = DatabaseConnector.get_db_instance()
            evaluation_model = db_instance.get_evaluation_result_by_id('project_id', self.project_id)
            evaluation_data = evaluation_model['result_data']
            evaluation_data['timestamp'] = datetime.datetime.now().timestamp()
            evaluation_data['train_results'] = results_train
            evaluation_data['test_results'] = results_test
            db_instance.add_or_update_evaluation_result(self.project_id, evaluation_data)

            self.monitor.finished()
        except Exception as e:
            print(e)
            self.monitor.failed()

    ######################################
    # Initialization                     #
    ######################################

    def _get_tasks(self):
        tasks = []
        tasks.append({'name': 'Graph sampling'})
        tasks.append({'name': 'Get missing edges'})

        for predictor in self.predictors:
            if predictor['feature_type'] == "Topology":
                predictor_name = predictor['designation']
                name = f'Calculate {predictor_name}'
                tasks.append({'name': name})

        socialtheory_categories = [
            'Social Theory with endogenous Attributes',
            'Social Theory with exogenous Attributes',
            'SocialTheoryEnsemble'
        ]
        for predictor in self.predictors:
            if predictor['feature_type'] in socialtheory_categories:
                predictor_name = predictor['designation']
                name = f'Calculate {predictor_name}'
                tasks.append({'name': name})

        for predictor in self.predictors:
            if predictor['feature_type'] == "ML-Classifier":
                predictor_name = predictor['designation']
                name = f'Train {predictor_name}'
                tasks.append({'name': name})

        for predictor in self.predictors:
            if predictor['feature_type'] == "ML-Classifier":
                predictor_name = predictor['designation']
                name = f'Predict {predictor_name}'
                tasks.append({'name': name})

        tasks.append({'name': 'Create predicted graph'})
        tasks.append({'name': 'Create evaluation results'})

        return tasks

    ######################################
    # Pipeline - Preparation             #
    ######################################

    def _sample_graphs(self, ground_truth_graph):
        self.monitor.notify('Processing')

        train_graph, test_graph = None, None
        if self.validation:
            test_ratio = self.test_split
            train_ratio = self.train_split
            test_graph = sampling_by_percentage(ground_truth_graph, test_ratio)
            train_graph = sampling_by_percentage(test_graph, train_ratio)
        else:
            train_ratio = self.train_split
            train_graph = sampling_by_percentage(ground_truth_graph, train_ratio)

        self.monitor.notify('Finished')
        return (train_graph, test_graph)

    def _get_missing_edges(self, ground_truth_graph, train_graph, test_graph):
        self.monitor.notify('Processing')

        train_missing_edges, test_missing_edges = None, None
        if self.validation:
            train_missing_edges = find_all_missing_edges(train_graph)
            test_missing_edges = find_all_missing_edges(test_graph)
        else:
            train_missing_edges = find_all_missing_edges(train_graph)

        self.monitor.notify('Finished')
        return (train_missing_edges, test_missing_edges)

    def _prepare_labels(self, ground_truth_graph, test_graph, train_missing_edges, test_missing_edges):
        train_set, test_set = None, None
        if self.validation:
            train_set = assign_labels(train_missing_edges, test_graph)
            test_set = assign_labels(test_missing_edges, ground_truth_graph)
        else:
            train_set = assign_labels(train_missing_edges, ground_truth_graph)

        return (train_set, test_set)

    ######################################
    # Pipeline - Topology                #
    ######################################

    def _topology_pipeline(self, ground_truth_graph, train_graph, test_graph, train_set, test_set):
        train_predictors, test_predictors = self._create_topology_predictors(train_graph, test_graph)
        predictors_columnsheader = self._get_topology_columnsheader()
        X_train, X_test = self._calculate_topology_features(train_predictors, test_predictors, train_set, test_set)
        train_df, test_df = self._create_topology_df(X_train, X_test, train_set, test_set, predictors_columnsheader)
        print("_topology_pipeline")
        return (train_df, test_df)

    def _create_topology_predictors(self, train_graph, test_graph):
        train_predictors, test_predictors = None, None
        if self.validation:
            train_predictors = list(map(partial(self._to_topology_predictor, graph=train_graph),
                                        [predictor for predictor in self.predictors
                                         if predictor['feature_type'] == "Topology"]))

            test_predictors = list(map(partial(self._to_topology_predictor, graph=test_graph),
                                       [predictor for predictor in self.predictors
                                        if predictor['feature_type'] == "Topology"]))
        else:
            train_predictors = list(map(partial(self._to_topology_predictor, graph=train_graph),
                                        [predictor for predictor in self.predictors
                                         if predictor['feature_type'] == "Topology"]))
        print("_create_topology_predictors")
        return (train_predictors, test_predictors)

    def _get_topology_columnsheader(self):        
        print(" _get_topology_columnsheader")
        return [predictor['designation'] for predictor in self.predictors
                if predictor['feature_type'] == "Topology"]

    def _calculate_topology_features(self, train_predictors, test_predictors, train_set, test_set):
        train_features, test_features = None, None
        if self.validation:
            train_node_pairs = train_set.node_pairs.values
            test_node_pairs = test_set.node_pairs.values
            train_features = []
            test_features = []
            for train_predictor, test_predictor in zip(train_predictors, test_predictors):
                self.monitor.notify('Processing')
                train_features.append(get_prediction(train_node_pairs, train_predictor))
                test_features.append(get_prediction(test_node_pairs, test_predictor))
                self.monitor.notify('Finished')
        else:
            train_node_pairs = train_set.node_pairs.values
            train_features = []
            for train_predictor in train_predictors:
                self.monitor.notify('Processing')
                train_features.append(get_prediction(train_node_pairs, train_predictor))
                self.monitor.notify('Finished')
        print("_calculate_topology_features")
        return (train_features, test_features)

    def _create_topology_df(self, train_preds, test_preds, train_set, test_set, columns_header):
        train_final, test_final = None, None
        if self.validation:
            train_df = get_dataframe(train_preds, columns_header)
            test_df = get_dataframe(test_preds, columns_header)
            train_final = pd.concat([train_set, train_df], axis=1)
            test_final = pd.concat([test_set, test_df], axis=1)
        else:
            train_df = get_dataframe(train_preds, columns_header)
            train_final = pd.concat([train_set, train_df], axis=1)
        print("_create_topology_df")
        return (train_final, test_final)

    def _add_topology_to_predicted_graph(self, train_t_df, test_t_df, predicted_graph_train, predicted_graph_test):
        if self.validation:
            columns_header = self._get_topology_columnsheader()
            thresholds = self._get_topology_thresholds(test_t_df, columns_header)
            print("start _add_topology_to_predicted_graph 1")
            for index, row in test_t_df.iterrows():
                node_pair = row['node_pairs']
                for col in columns_header:
                    if row[col] > thresholds[col]:
                        add_or_update_edge(
                            graph=predicted_graph_test,
                            edge=(node_pair[0], node_pair[1]),
                            method_name='Topology',
                            method_specified=str(col),
                            score=row[col])   
            print("done with outer loop in 1")
            
        else:
            columns_header = self._get_topology_columnsheader()
            thresholds = self._get_topology_thresholds(train_t_df, columns_header)
            print("start _add_topology_to_predicted_graph 2")
            for index, row in train_t_df.iterrows():
                node_pair = row['node_pairs']
                for col in columns_header:
                    if row[col] > thresholds[col]:
                        add_or_update_edge(
                            graph=predicted_graph_train,
                            edge=(node_pair[0], node_pair[1]),
                            method_name='Topology',
                            method_specified=str(col),
                            score=row[col])   
            print("done with outer loop in 2")

    def _get_topology_thresholds(self, df, columns_header):
        false_predictions_df = df[df['label'] == 0]
        false_predictions_df = false_predictions_df[columns_header]
        print("_get_topology_thresholds")
        return false_predictions_df.max()

    ######################################
    # Pipeline - SocialTheory            #
    ######################################

    def _socialtheory_pipeline(self, train_graph, test_graph, train_set, test_set, predicted_graph_train, predicted_graph_test):
        train_predictors, test_predictors = self._create_socialtheory_predictors(train_graph, test_graph, predicted_graph_train, predicted_graph_test)
        train_df, test_df = self._calculate_socialtheory_features(train_predictors, test_predictors, train_set, test_set, predicted_graph_train, predicted_graph_test)
        return (train_df, test_df)

    def _create_socialtheory_predictors(self, train_graph, test_graph, predicted_train_graph, predicted_test_graph):
        train_predictors, test_predictors = None, None
        if self.validation:
            threshold_train, threshold_test = None, None
            for predictor in self.predictors:
                if predictor['feature_type'] == "Social Theory with exogenous Attributes":
                    threshold_train = get_attribute_threshold(train_graph, predictor['parameters']['attribute_weightings'])
                    threshold_test = get_attribute_threshold(test_graph, predictor['parameters']['attribute_weightings'])
                if not threshold_train is None:
                    break
            train_predictors = list(map(partial(self._to_socialtheory_predictor, graph=train_graph, predicted_graph=predicted_train_graph, threshold=threshold_train),
                                        [predictor for predictor in self.predictors
                                         if (predictor['feature_type'] == "Social Theory with endogenous Attributes") or
                                            (predictor['feature_type'] == "Social Theory with exogenous Attributes")]))

            test_predictors = list(map(partial(self._to_socialtheory_predictor, graph=test_graph, predicted_graph=predicted_test_graph, threshold=threshold_test),
                                       [predictor for predictor in self.predictors
                                        if (predictor['feature_type'] == "Social Theory with endogenous Attributes") or
                                           (predictor['feature_type'] == "Social Theory with exogenous Attributes")]))
        else:
            threshold_train = None
            for predictor in self.predictors:
                if predictor['feature_type'] == "Social Theory with exogenous Attributes":
                    threshold_train = get_attribute_threshold(train_graph, predictor['parameters']['attribute_weightings'])
                if not threshold_train is None:
                    break
            train_predictors = list(map(partial(self._to_socialtheory_predictor, graph=train_graph, predicted_graph=predicted_train_graph, threshold=threshold_train),
                                        [predictor for predictor in self.predictors
                                         if (predictor['feature_type'] == "Social Theory with endogenous Attributes") or
                                            (predictor['feature_type'] == "Social Theory with exogenous Attributes")]))

        return (train_predictors, test_predictors)

    def _calculate_socialtheory_features(self, train_predictors, test_predictors, train_set, test_set, predicted_train_graph, predicted_test_graph):
        train_features, test_features = None, None
        if self.validation:
            train_node_pairs = train_set.node_pairs.values
            test_node_pairs = test_set.node_pairs.values
            df_train, df_test = None, None
            for train_predictor, test_predictor in zip(train_predictors, test_predictors):
                self.monitor.notify('Processing')
                train_predictor.predict(train_node_pairs)
                test_predictor.predict(test_node_pairs)
                self.monitor.notify('Finished')
            df_train = get_st_features_from_predicted_graph(predicted_train_graph, train_node_pairs).drop('node_pairs', axis=1)
            df_test = get_st_features_from_predicted_graph(predicted_test_graph, test_node_pairs).drop('node_pairs', axis=1)
        else:
            train_node_pairs = train_set.node_pairs.values
            df_train, df_test = None, None
            for train_predictor in train_predictors:
                self.monitor.notify('Processing')
                train_predictor.predict(train_node_pairs)
                self.monitor.notify('Finished')
            df_train = get_st_features_from_predicted_graph(predicted_train_graph, train_node_pairs).drop('node_pairs', axis=1)
        return (df_train, df_test)

    ######################################
    # Pipeline - Classification          #
    ######################################

    def _classification_pipeline(self, train_df, test_df):
        # Remove balance theories from descriptive features due to inconsistence
        train_df_without_balance = train_df.drop(list(train_df.filter(regex='BalanceTheory')), axis=1)
        test_df_without_balance = None
        if not test_df is None:
            test_df_without_balance = test_df.drop(list(train_df.filter(regex='BalanceTheory')), axis=1)

        if self.validation and self.preprocessing:
            train_df = preprocess_df(train_df_without_balance)

        X_train, y_train, X_test, y_test = self._get_X_y(train_df, test_df)
        X_train_wb, y_train_wb, X_test_wb, y_test_wb = self._get_X_y(train_df_without_balance, test_df_without_balance)
        classifiers = self._create_classifiers()
        columnsheader = self._create_classifiers_columnsheader()
        self._train_classifiers(X_train_wb, y_train_wb, classifiers)
        y_train_predictions, y_test_predictions = self._classifier_predictions(X_train_wb, X_test_wb, classifiers)

        predictions_train_df = pd.concat([X_train, pd.DataFrame(y_train_predictions, columns=columnsheader)], axis=1)
        predictions_test_df = None
        if not y_test_predictions is None:
            predictions_test_df = pd.concat([X_test, pd.DataFrame(y_test_predictions, columns=columnsheader)], axis=1)
        else:
            predictions_test_df = X_test

        return (predictions_train_df, predictions_test_df)

    def _get_X_y(self, train_df, test_df):
        X_train, X_test, y_train, y_test = None, None, None, None
        if self.validation:
            X_train, y_train = get_X_y(train_df)
            X_test, y_test = get_X_y(test_df)
        else:
            X_train, y_train = get_X_y(train_df)

        return (X_train, y_train, X_test, y_test)

    def _create_classifiers(self):
        classifiers = list(map(self._to_classifier,
                               [predictor for predictor in self.predictors
                                if predictor['feature_type'] == "ML-Classifier"]))

        return classifiers

    def _create_classifiers_columnsheader(self):
        return [predictor['designation'] for predictor in self.predictors
                if predictor['feature_type'] == "ML-Classifier"]

    def _train_classifiers(self, X_train, y_train, classifiers):
        if len(classifiers) <= 0:
            return

        for classifier in classifiers:
            self.monitor.notify('Processing')
            classifier.fit(X_train, y_train)
            self.monitor.notify('Finished')

    def _classifier_predictions(self, X_train, X_test, classifiers):
        if len(classifiers) <= 0:
            return ([], [] if self.validation else None)
        
        predictions_train, predictions_test = None, None
        if self.validation:
            predictions_train = []
            predictions_test = []
            for classifier in classifiers:
                self.monitor.notify('Processing')
                prediction_train = classifier.predict_proba(X_train)
                prediction_test = classifier.predict_proba(X_test)
                predictions_train.append(prediction_train[:, 1] if (prediction_train.shape[1] == 2) else prediction_train)
                predictions_test.append(prediction_test[:, 1] if (prediction_test.shape[1] == 2) else prediction_test)
                self.monitor.notify('Finished')
            predictions_train = np.column_stack(prediction for prediction in predictions_train)
            predictions_test = np.column_stack(prediction for prediction in predictions_test)
        else:
            predictions_train = []
            for classifier in classifiers:
                self.monitor.notify('Processing')
                prediction_train = classifier.predict_proba(X_train)
                predictions_train.append(prediction_train[:, 1] if (prediction_train.shape[1] == 2) else prediction_train)
                self.monitor.notify('Finished')
            predictions_train = np.column_stack(prediction for prediction in predictions_train)

        return (predictions_train, predictions_test)

    def _add_classification_to_predicted_graph(self, node_pairs, train_c_df, test_c_df, predicted_graph_train, predicted_graph_test):
        if self.validation:
            columns_header = self._create_classifiers_columnsheader()
            test_c_df = pd.concat([node_pairs, test_c_df], axis=1)
            for index, row in test_c_df.iterrows():
                node_pair = row['node_pairs']
                for col in columns_header:
                    if row[col] >= 0.5:
                        add_or_update_edge(
                            graph=predicted_graph_test,
                            edge=(node_pair[0], node_pair[1]),
                            method_name='ML-Classification',
                            method_specified=col,
                            score=row[col]
                        )                 
        else:
            columns_header = self._create_classifiers_columnsheader()
            train_c_df = pd.concat([node_pairs, train_c_df], axis=1)
            for index, row in train_c_df.iterrows():
                node_pair = row['node_pairs']
                for col in columns_header:
                    if row[col] >= 0.5:
                        add_or_update_edge(
                            graph=predicted_graph_train,
                            edge=(node_pair[0], node_pair[1]),
                            method_name='ML-Classification',
                            method_specified=col,
                            score=row[col]
                        )

    ######################################
    # Pipeline - Evaluation              #
    ######################################

    def _create_results(self, predictions_train_df, predictions_test_df):
        self.monitor.notify('Processing')
        if self.validation:
            results_train = {}
            results_test = {}
            labels_train = predictions_train_df['label']
            labels_test = predictions_test_df['label']
            predictions_train = predictions_train_df.drop(['node_pairs', 'label'], axis=1)
            predictions_test = predictions_test_df.drop(['node_pairs', 'label'], axis=1)
            for predictor in predictions_train.columns:
                roc_train = ROC(labels_train.values, predictions_train[predictor].values)
                auc_train = AUC(labels_train.values, predictions_train[predictor].values)
                roc_test = ROC(labels_test.values, predictions_test[predictor].values)
                auc_test = AUC(labels_test.values, predictions_test[predictor].values)
                results_train[predictor] = get_metrics_as_json([roc_train, auc_train])
                results_test[predictor] = get_metrics_as_json([roc_test, auc_test])

            self.monitor.notify('Finished')
            return (results_train, results_test)
        else:
            results_train = {}
            labels_train = predictions_train_df['label']
            predictions_train = predictions_train_df.drop(['node_pairs', 'label'], axis=1)
            for predictor in predictions_train.columns:
                roc = ROC(labels_train.values, predictions_train[predictor].values)
                auc = AUC(labels_train.values, predictions_train[predictor].values)
                results_train[predictor] = get_metrics_as_json([roc, auc])
            
            self.monitor.notify('Finished')
            return (results_train, None)

    ######################################
    # MISC                               #
    ######################################

    def _save_predicted_graph(self, predicted_graph_train, predicted_graph_test):
        self.monitor.notify('Processing')

        pred_net = DatabaseConnector.get_db_instance().get_predicted_network_by_id('project_id', self.project_id)
        if self.validation:
            save_predicted_graph_to_db(predicted_graph_test, pred_net['predicted_network_id'])
        else:
            save_predicted_graph_to_db(predicted_graph_train, pred_net['predicted_network_id'])

        self.monitor.notify('Finished')

    def _to_topology_predictor(self, model, graph):
        return self.factory.create(model, graph=graph)

    def _to_socialtheory_predictor(self, model, graph, predicted_graph, threshold):
        return self.factory.create(model, graph=graph, predicted_graph=predicted_graph, threshold=threshold)

    def _to_classifier(self, model):
        return self.factory.create(model)
