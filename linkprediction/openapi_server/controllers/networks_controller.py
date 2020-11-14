import connexion
import six

from linkprediction.openapi_server.models.original_network import OriginalNetwork  # noqa: E501
from linkprediction.openapi_server.models.predicted_network import PredictedNetwork  # noqa: E501
from linkprediction.openapi_server import util

from linkprediction.database_connector import DatabaseConnector
from linkprediction.graph_import.predicted_graph_handler import load_predicted_graph_from_db


def delete_original_network_by_project(project_id):  # noqa: E501
    """Delete original network by a project ID.

    Deletes the original network of a project. # noqa: E501

    :param project_id: ID of the current project.
    :type project_id: 

    :rtype: None
    """
    try:
        db = DatabaseConnector.get_db_instance()
        db.delete_original_network_by_id('project_id', project_id)
        return f'Deleted original network with ProjectID {project_id}'
    except Exception as error:
        return ('Exception', error)


def delete_predicted_network_by_project(project_id):  # noqa: E501
    """Delete predicted network of by a project ID.

    Deletes predicted network of a project. # noqa: E501

    :param project_id: ID of the current project.
    :type project_id: 

    :rtype: None
    """
    try:
        db = DatabaseConnector.get_db_instance()
        db.delete_predicted_network_by_id('project_id', project_id)
        return f'Deleted predicted network with ProjectID {project_id}'
    except Exception as error:
        return ('Exception', error)


def get_original_network_by_project(project_id):  # noqa: E501
    """Find original network by a project ID.

    Returns the original network. # noqa: E501

    :param project_id: ID of the current project.
    :type project_id: 

    :rtype: OriginalNetwork
    """
    try:
        db = DatabaseConnector.get_db_instance()
        original_network = db.get_original_network_by_id(
            'project_id',
            project_id
        )
        nodes = db.get_nodes_by_id(
            'original_network_id',
            original_network['original_network_id']
        )
        edges = db.get_edges_of_original_network_by_id(
            'original_network_id',
            original_network['original_network_id']
        )
        return OriginalNetwork(
            id=original_network['original_network_id'],
            designation=original_network['designation'],
            directed=original_network['directed'],
            multigraph=original_network['multigraph'],
            node_count=len(nodes),
            edge_count=len(edges)
        )
    except Exception as error:
        return ('Exception', error)


def get_predicted_network_by_project(project_id):  # noqa: E501
    """Find predicted network by a project ID.

    Returns the predicted network. # noqa: E501

    :param project_id: ID of the current project.
    :type project_id: 

    :rtype: PredictedNetwork
    """
    try:
        db = DatabaseConnector.get_db_instance()
        predicted_network = db.get_predicted_network_by_id(
            'project_id',
            project_id
        )

        predicted_graph = load_predicted_graph_from_db(predicted_network['predicted_network_id'])

        return PredictedNetwork(
            nodes=predicted_graph['nodes'],
            links=predicted_graph['links'],
            information=predicted_graph['information']
        )
    except Exception as error:
        return ('Exception', error)
