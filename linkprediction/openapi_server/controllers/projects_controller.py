import logging

import werkzeug.exceptions as http_exceptions

from linkprediction.database_connector import DatabaseConnector
from linkprediction.graph_import.network_file import NetworkFile
from linkprediction.graph_import.original_graph_handler import build_original_graph
from linkprediction.graph_import.predicted_graph_handler import save_predicted_graph_to_db
from linkprediction.openapi_server.models.project import Project  # noqa: E501
from linkprediction.openapi_server.models.evaluation_setup import EvaluationSetup  # noqa: E501


def create_project(**kwargs):  # noqa: E501
    """Creates a project with an original network file.

    Creates a project with an original network file. # noqa: E501

    :param designation:
    :type designation: str
    :param description:
    :type description: str
    :param network_designation:
    :type network_designation: str
    :param network_directed:
    :type network_directed: bool
    :param network_multigraph:
    :type network_multigraph: bool
    :param network_file: Binary object which contains the network file with a standard network format.
    :type network_file: str
    :param additional_network_file: Binary object which contains an additional network file with a standard network format (especailly used for CSV imports).
    :type additional_network_file: str
    :param file_format:
    :type file_format: str

    :rtype: Project
    """
    body = dict(kwargs.items()).get('body')
    file = dict(kwargs.items()).get('network_file')
    additional_file = dict(kwargs.items()).get('additional_network_file')
    # Try to process and safe the file before accessing the Database
    try:
        file_format = body.get('file_format')
        network_file = NetworkFile(file_format, file, additional_file)
        node_list = network_file.parse_nodes()
    except Exception:
        logging.exception("Exception while handling the input file")
        e = http_exceptions.InternalServerError(
            description='Something went wrong! Please check if your network file is correct.')
        raise e

    try:
        db = DatabaseConnector.get_db_instance()
        project_id = db.add_project(
            designation=body.get('designation'),
            description=body.get('description')
        )
        original_network_id = db.add_original_network_to_project(
            designation=body.get('network_designation'),
            directed=body.get('network_directed'),
            multigraph=body.get('network_multigraph'),
            project_id=project_id
        )
        predicted_network_id = db.add_predicted_network_to_project(
            designation=body.get('network_designation'),
            project_id=project_id
        )
        nodes = db.add_nodes(node_list, original_network_id, predicted_network_id)
        edge_list = network_file.parse_edges(nodes)
        db.add_edges_to_original_network(edge_list, original_network_id)
        for node in nodes:
            attribute_list = network_file.parse_attributes(node[0])
            if attribute_list:
                db.add_node_attributes(attribute_list, node[1])

        graph = build_original_graph('project_id', project_id)
        save_predicted_graph_to_db(graph.copy(), predicted_network_id)

        default_evaluation_setup = {
            "random_seed": 42,
            "with_validation": False,
            "train_sampling_ratio": 0.8,
            "test_sampling_ratio": 0.9,
            "ml_preprocessing": False
        }
        db.add_or_update_evaluation_result(project_id, default_evaluation_setup)

        return Project(
            id=project_id,
            designation=body.get('designation'),
            description=body.get('description'),
            original_network_id=original_network_id,
            predicted_network_id=predicted_network_id
        )
    except Exception:
        logging.exception("Exception occured while inserting data in the database")
        e = http_exceptions.InternalServerError(
            description='Something went wrong! The input file seems to be wrong and the data could not be loaded into the database.')
        raise e


def delete_project_by_id(project_id):  # noqa: E501
    """Delete project by an ID.

    Deletes a project by an ID. # noqa: E501

    :param project_id: ID of the project to delete.
    :type project_id:

    :rtype: None
    """
    try:
        db = DatabaseConnector.get_db_instance()
        db.delete_project(project_id)
        return f'Deleted project with ID {project_id}'
    except Exception as error:
        return ('Exception', error)


def get_project_by_id(project_id):  # noqa: E501
    """Find project by an ID.

    Returns a project by an ID. # noqa: E501

    :param project_id: ID of the project to return.
    :type project_id:

    :rtype: Project
    """
    try:
        db = DatabaseConnector.get_db_instance()
        project_data = db.get_project_by_id('project_id', project_id)
        return Project(
            id=project_data['project_id'],
            designation=project_data['designation'],
            description=project_data['description'],
            original_network_id=project_data['original_network_id']
            # predicted_network_id
        )
    except Exception as error:
        return ('Exception', error)


def get_projects():  # noqa: E501
    """Returns a list of available projects.

    Get all projects as an array. # noqa: E501


    :rtype: List[Project]
    """
    try:
        db = DatabaseConnector.get_db_instance()
        projects_data = db.get_projects()

        project_instances = []
        for project_data in projects_data:
            project_instances.append(
                Project(
                    id=project_data['project_id'],
                    designation=project_data['designation'],
                    description=project_data['description'],
                    original_network_id=project_data['original_network_id'],
                    predicted_network_id=project_data['predicted_network_id']
                )
            )
        return project_instances
    except Exception as error:
        return ('Exception', error)


def update_project_by_id(**kwargs):  # noqa: E501
    """Update project by an ID.

    Updates a project by an ID. # noqa: E501

    :param project_id: ID of the project to update.
    :type project_id:
    :param designation:
    :type designation: str
    :param description:
    :type description: str
    :param network_designation:
    :type network_designation: str
    :param network_directed:
    :type network_directed: bool
    :param network_multigraph:
    :type network_multigraph: bool
    :param network_file: Binary object which contains the network file with a standard network format.
    :type network_file: str
    :param file_format:
    :type file_format: str

    :rtype: Project
    """

    return 'do some magic!'
