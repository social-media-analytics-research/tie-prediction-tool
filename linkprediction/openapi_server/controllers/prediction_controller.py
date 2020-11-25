import connexion
import six
import json
import multiprocessing

from linkprediction.openapi_server.models.evaluation_results import EvaluationResults  # noqa: E501
from linkprediction.openapi_server.models.prediction_setup import PredictionSetup  # noqa: E501
from linkprediction.openapi_server.models.prediction_state import PredictionState  # noqa: E501
from linkprediction.openapi_server.models.prediction_status import PredictionStatus  # noqa: E501
from linkprediction.openapi_server.models.predictors import Predictors  # noqa: E501
from linkprediction.openapi_server.models.predictors import Predictor  # noqa: E501
from linkprediction.openapi_server.models.predictors import EvaluationSetup  # noqa: E501
from linkprediction.openapi_server import util

from linkprediction.database_connector import DatabaseConnector
from linkprediction.prediction_methods.prediction_worker import PredictionWorker
from linkprediction.prediction_methods.prediction.social_theory import ATTR_HANDLING

prediction_process = multiprocessing.Process()

def create_prediction_setup(project_id, body):  # noqa: E501
    """Creates a prediction.

    Creates a predictors setup. # noqa: E501

    :param project_id: ID of the current project.
    :type project_id: 
    :param prediction_setup: 
    :type prediction_setup: dict | bytes

    :rtype: None
    """
    try:
        db_instance = DatabaseConnector.get_db_instance()
        predicted_network = db_instance.get_predicted_network_by_id(
            'project_id',
            project_id
        )
        predicted_network_id = predicted_network['predicted_network_id']

        for predictor in body['selected_predictors']:
            db_instance.add_selected_network_feature_to_project(
                designation=predictor["designation"],
                feature_type=predictor["category"],
                parameters=predictor["parameters"],
                predicted_network_id=predicted_network_id
            )

        evaluation_setup_old = db_instance.get_evaluation_result_by_id('project_id', project_id)
        evaluation_setup = body['evaluation_setup']
        if 'train_results' in evaluation_setup_old['result_data']:
            evaluation_setup['train_results'] = evaluation_setup_old['result_data']['train_results']
            evaluation_setup['test_results'] = evaluation_setup_old['result_data']['test_results']
            evaluation_setup['timestamp'] = evaluation_setup_old['result_data']['timestamp']

        db_instance.add_or_update_evaluation_result(
            project_id, json.dumps(evaluation_setup))
        return 'Created prediction!'
    except Exception as error:
        return ('Exception', error)


def delete_prediction_setup(project_id):  # noqa: E501
    """Delete selected prediction setup of a project.

    Delete prediction setup of a project. # noqa: E501

    :param project_id: ID of the current project.
    :type project_id: 

    :rtype: None
    """
    try:
        db_instance = DatabaseConnector.get_db_instance()
        predicted_network = db_instance.get_predicted_network_by_id(
            'project_id',
            project_id
        )
        predicted_network_id = predicted_network['predicted_network_id']

        prediction_features = db_instance.get_selected_network_features_by_id(
            'predicted_network_id',
            predicted_network_id
        )
        for predictor in prediction_features:
            db_instance.delete_selected_network_features_by_id(
                'predicted_network_id',
                predicted_network_id
            )
        return 'Deleted prediction features!'
    except Exception as error:
        return ('Exception', error)


def get_evaluation_results_by_project(project_id):  # noqa: E501
    """Find evaluation results by project ID.

    Returns evaluation results of a project. # noqa: E501

    :param project_id: ID of the current project.
    :type project_id: 

    :rtype: EvaluationResults
    """
    try:
        db_instance = DatabaseConnector.get_db_instance()
        evaluation_result = db_instance.get_evaluation_result_by_id(
            'project_id',
            project_id
        )

        timestamp = None
        if 'timestamp' in evaluation_result['result_data']:
            timestamp = evaluation_result['result_data']['timestamp']

        return EvaluationResults(
            timestamp=timestamp,
            results=evaluation_result['result_data']
        )
    except Exception as error:
        return ('Exception', error)



def get_prediction_status_by_project(project_id):  # noqa: E501
    """Find prediction status by a project ID.

    Returns the current prediction state. # noqa: E501

    :param project_id: ID of the current project.
    :type project_id: 

    :rtype: PredictionStatus
    """
    try:
        db_instance = DatabaseConnector.get_db_instance()
        predicted_network = db_instance.get_predicted_network_by_id(
            'project_id',
            project_id
        )
        
        predicted_network_id = predicted_network['predicted_network_id']

        prediction_status = db_instance.get_last_linkprediction_status_by_id('predicted_network_id', predicted_network_id)

        return PredictionStatus(
            prediction_status['status_id'],
            prediction_status['log_timestamp'],
            prediction_status['current_step'],
            prediction_status['max_steps'],
            prediction_status['process_step'],
            prediction_status['status_value']
        )
    except Exception as error:
        return ('Exception', error)


def get_predictors_by_project(project_id):  # noqa: E501
    """Find predictors by project ID.

    Returns all available and selected predictors # noqa: E501

    :param project_id: ID of the current project.
    :type project_id: 

    :rtype: Predictors
    """
    try:
        db_instance = DatabaseConnector.get_db_instance()
        predicted_network = db_instance.get_predicted_network_by_id(
            'project_id',
            project_id
        )
        predicted_network_id = predicted_network['predicted_network_id']
        standard_features = db_instance.get_standard_network_features()
        standard_feature_list = []
        exogenous_attributes = db_instance.get_distinct_node_attributes_by_id(
            'project_id',
            project_id
        )
        exogenous_attributes = [
            attr for attr in exogenous_attributes
            if attr in ATTR_HANDLING and ATTR_HANDLING[attr] is not None
        ]
        exogenous_attributes_params = [
            {'attribute': attr, 'value': 1} for attr in exogenous_attributes
        ]

        for standard_feature in standard_features:
            if standard_feature['feature_type'] == 'Social Theory with exogenous Attributes':
                standard_feature['parameters']['attribute_weightings'] = exogenous_attributes_params
            standard_feature_list.append(
                Predictor(
                    id=standard_feature['standard_feature_id'],
                    designation=standard_feature['designation'],
                    category=standard_feature['feature_type'],
                    parameters=standard_feature['parameters']
                )
            )
        selected_features = db_instance.get_selected_network_features_by_id(
            id_type='predicted_network_id',
            reference_id=predicted_network_id
        )
        selected_feature_list = []
        for selected_feature in selected_features:
            selected_feature_list.append(
                Predictor(
                    id=selected_feature['selected_feature_id'],
                    designation=selected_feature['designation'],
                    category=selected_feature['feature_type'],
                    parameters=selected_feature['parameters']
                )
            )
        return Predictors(
            available_predictors=standard_feature_list,
            selected_predictors=selected_feature_list,
            evaluation_setup=EvaluationSetup(
                random_seed=42,
                with_validation=False,
                train_sampling_ratio=0.7
            )
        )
    except Exception as error:
        return ('Exception', error)


def handle_prediction_state_by_project(project_id, body):  # noqa: E501
    """Handles the state of the prediction of a project.

    Handles the prediction state. # noqa: E501

    :param project_id: ID of the current project.
    :type project_id: 
    :param prediction_state: 
    :type prediction_state: dict | bytes

    :rtype: PredictionStatus
    """
    if connexion.request.is_json:
        prediction_state = PredictionState.from_dict(connexion.request.get_json())  # noqa: E501

    try:
        db_instance = DatabaseConnector.get_db_instance()
        project = db_instance.get_project_by_id('project_id', project_id)
        predicted_network_id = project['predicted_network_id']

        #Note: Currently only working for one request. For parallel advanced
        # handling (task queues, etc) necessary.
        global prediction_process
        if prediction_state.state == "Start":
            print("BEGIN PREDICTION PRCOESS")
            predictors = db_instance.get_selected_network_features_by_id(
                'predicted_network_id', predicted_network_id)
            evaluation = db_instance.get_evaluation_result_by_id(
                'project_id', project_id)
            configuration = evaluation['result_data']
            worker = PredictionWorker(
                0,
                project_id,
                predictors,
                configuration['with_validation'],
                configuration['ml_preprocessing'],
                configuration['train_sampling_ratio'],
                configuration['test_sampling_ratio'],
                configuration['random_seed'])

            prediction_process = multiprocessing.Process(target=worker.predict, daemon=True)

            DatabaseConnector.get_db_instance().add_linkprediction_status(
                0,
                0,
                0,
                'Prediction',
                'Waiting',
                'project_id',
                project_id
            )

            prediction_process.start()
        elif prediction_state.state == "Abort":
            print("ABORT PREDICTION PRCOESS")
            prediction_process.terminate()
            db_instance.add_linkprediction_status(
            0, 
            0, 
            0, 
            "Prediction", 
            "Failed", 
            'project_id',
            project_id)
    except Exception as error:
        return ('Exception', error)

    return 'Prediction state altered!'