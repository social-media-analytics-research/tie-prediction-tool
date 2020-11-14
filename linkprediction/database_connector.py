from __future__ import annotations

import logging
from datetime import datetime

import numpy
from psycopg2 import sql
from psycopg2.extensions import AsIs, register_adapter
from psycopg2.extras import Json, RealDictCursor
from psycopg2.pool import ThreadedConnectionPool


def adapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)


def adapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)


register_adapter(numpy.float64, adapt_numpy_float64)
register_adapter(numpy.int64, adapt_numpy_int64)


class MissingDataError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


def exception_decorator(wrapped_function):
    def _wrapper(*args, **kwargs):
        try:
            result = wrapped_function(*args, **kwargs)
        except Exception as error:
            logging.getLogger('database_connector').exception(
                'Exception occurred in %s.', wrapped_function.__name__
            )
            raise type(error)(
                f'Exception occurred in {wrapped_function.__name__}: {str(error)}'
            )
        return result
    return _wrapper


class DatabaseConnector:

    db_instance = None

    @classmethod
    def get_db_instance(cls) -> DatabaseConnector:
        if cls.db_instance is None:
            cls.db_instance = cls()
        return cls.db_instance

    def __init__(self):
        self.logger = logging.getLogger('database_connector')
        try:
            self.pool = ThreadedConnectionPool(
                1, 10,
                user='postgres',
                password='12345',
                host='127.0.0.1',
                port='5432',
                database='postgres'
            )
            self.schema = 'linkprediction'
        except Exception:
            logging.getLogger('database_connector').exception(
                'Exception occurred while connecting to the database'
            )

    def _get_dict_cursor(self, conn):
        return conn.cursor(
            cursor_factory=RealDictCursor
        )

    def _get_connection(self):
        return self.pool.getconn()

    def _put_connection(self, conn):
        self.pool.putconn(conn)

    # ####################################
    # BERUFENET                          #
    # ####################################
    @exception_decorator
    def get_occupations_by_column(self, column_type, value):
        """
        column_type: possible values = ['record_id', 'job_id', 'job_title']
        value: value of the column_type
        """
        if column_type not in ['record_id', 'job_id', 'job_title']:
            raise ValueError('Parameter column_type is not valid!')
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = sql.SQL(
            "SELECT * FROM {}.berufenet WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, column_type)),
            *map(sql.Literal, (value,))
        )
        cur.execute(query)
        records = cur.fetchall()
        self._put_connection(conn)
        if records is None:
            raise MissingDataError('Select statement returned None.')
        return records

    @exception_decorator
    def get_occupation_by_hierarchy(self, field_of_activity, subject_area, column_type, value):
        """
        column_type: possible values = ['job_id', 'job_title']
        value: value of the column_type
        """
        if column_type not in ['job_id', 'job_title']:
            raise ValueError('Parameter column_type is not valid!')
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = sql.SQL(
            "SELECT * FROM {}.berufenet \
                WHERE field_of_activity = {} \
                and subject_area = {} \
                and {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema,)),
            *map(sql.Literal, (field_of_activity, subject_area)),
            *map(sql.Identifier, (column_type,)),
            *map(sql.Literal, (value,))
        )
        cur.execute(query)
        record = cur.fetchone()
        self._put_connection(conn)
        if record is None:
            raise MissingDataError('Select statement returned None.')
        return record

    # ####################################
    # PROJECTS                           #
    # ####################################
    @exception_decorator
    def add_project(self, designation, description):
        conn = self._get_connection()
        cur = conn.cursor()
        query = f'INSERT INTO {self.schema}.projects (designation, description) ' \
                'VALUES (%s, %s) ' \
                'RETURNING project_id;'
        params = (designation, description)
        cur.execute(query, params)
        record = cur.fetchone()
        conn.commit()
        self._put_connection(conn)
        return next(iter(record), None)

    @exception_decorator
    def get_project_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['project_id']
        reference_id: value of the id
        """
        if id_type not in ['project_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = sql.SQL(
            "SELECT * FROM {}.projects WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        record = cur.fetchone()
        self._put_connection(conn)
        if record is None:
            raise MissingDataError('Select statement returned None.')
        return record

    @exception_decorator
    def get_projects(self):
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = f'SELECT * FROM {self.schema}.projects;'
        cur.execute(query)
        records = cur.fetchall()
        self._put_connection(conn)
        if records is None:
            raise MissingDataError('Select statement returned None.')
        return records

    @exception_decorator
    def delete_project(self, project_id):
        conn = self._get_connection()
        cur = conn.cursor()
        query = f'DELETE FROM {self.schema}.projects WHERE project_id = %s'
        params = (project_id,)
        cur.execute(query, params)
        conn.commit()
        self._put_connection(conn)
        return cur.statusmessage

    @exception_decorator
    def set_original_network_of_project(self, project_id, original_network_id):
        conn = self._get_connection()
        cur = conn.cursor()
        query = f'UPDATE {self.schema}.projects ' \
                'SET original_network_id = %s ' \
                'WHERE project_id = %s'
        params = (original_network_id, project_id)
        cur.execute(query, params)
        conn.commit()
        self._put_connection(conn)

    @exception_decorator
    def set_predicted_network_of_project(self, project_id, predicted_network_id):
        conn = self._get_connection()
        cur = conn.cursor()
        query = f'UPDATE {self.schema}.projects ' \
                'SET predicted_network_id = %s ' \
                'WHERE project_id = %s'
        params = (predicted_network_id, project_id)
        cur.execute(query, params)
        conn.commit()
        self._put_connection(conn)

    # ####################################
    # ORIGINAL_NETWORK                   #
    # ####################################
    @exception_decorator
    def add_original_network_to_project(self, designation, directed, multigraph, project_id):
        conn = self._get_connection()
        cur = conn.cursor()
        query = f'INSERT INTO {self.schema}.original_network' \
                '(designation, directed, multigraph, project_id) ' \
                'VALUES (%s, %s, %s, %s) ' \
                'RETURNING original_network_id;'
        params = (designation, directed, multigraph, project_id)
        cur.execute(query, params)
        original_network_id = next(iter(cur.fetchone()), None)
        conn.commit()
        self._put_connection(conn)
        if original_network_id is not None:
            self.set_original_network_of_project(
                project_id, original_network_id)
        return original_network_id

    @exception_decorator
    def get_original_network_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['original_network_id', 'project_id']
        reference_id: value of the id
        """
        if id_type not in ['original_network_id', 'project_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = sql.SQL(
            "SELECT * FROM {}.original_network WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        record = cur.fetchone()
        self._put_connection(conn)
        if record is None:
            raise MissingDataError('Select statement returned None.')
        return record

    @exception_decorator
    def delete_original_network_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['original_network_id', 'project_id']
        reference_id: value of the id
        """
        if id_type not in ['original_network_id', 'project_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = conn.cursor()
        query = sql.SQL(
            "DELETE FROM {}.original_network WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        conn.commit()
        self._put_connection(conn)

    # ####################################
    # ORIGINAL_EDGES                    #
    # ####################################
    @exception_decorator
    def add_edges_to_original_network(self, edge_list, original_network_id):
        """
        edge_list: [(source_node: uuid, target_node: uuid)]
        original_network_id: uuid
        """
        conn = self._get_connection()
        cur = conn.cursor()
        args_str = ','.join(
            cur.mogrify(
                "(%s, %s, %s)",
                (source_node, target_node, original_network_id)
            ).decode("utf-8")
            for source_node, target_node in edge_list)
        cur.execute(
            f'INSERT INTO {self.schema}.original_edges '
            '(source_node, target_node, original_network_id) '
            f'VALUES {args_str} '
            'RETURNING original_edge_id;'
        )
        records = [next(iter(record))
                   for record in cur.fetchall() if len(record) > 0]
        conn.commit()
        self._put_connection(conn)
        return records

    @exception_decorator
    def get_edges_of_original_network_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['original_edge_id', 'original_network_id', 'project_id']
        reference_id: value of the id
        """
        if id_type not in ['original_edge_id', 'original_network_id', 'project_id']:
            raise ValueError('Parameter id_type is not valid!')
        if id_type == 'project_id':
            original_network = self.get_original_network_by_id('project_id', reference_id)
            id_type = 'original_network_id'
            reference_id = original_network['original_network_id']
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = sql.SQL(
            "SELECT * FROM {}.original_edges WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        records = cur.fetchall()
        self._put_connection(conn)
        if records is None:
            raise MissingDataError('Select statement returned None.')
        return records

    @exception_decorator
    def delete_edges_of_original_network_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['original_edge_id', 'original_network_id', 'project_id']
        reference_id: value of the id
        """
        if id_type not in ['original_edge_id', 'original_network_id', 'project_id']:
            raise ValueError('Parameter id_type is not valid!')
        if id_type == 'project_id':
            reference_id = self.get_original_network_by_id('project_id', reference_id)
            id_type = 'original_network_id'
        conn = self._get_connection()
        cur = conn.cursor()
        query = sql.SQL(
            "DELETE FROM {}.original_edges WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        conn.commit()
        self._put_connection(conn)

    # ####################################
    # PREDICTED_NETWORK                  #
    # ####################################
    @exception_decorator
    def add_predicted_network_to_project(self, designation, project_id):
        conn = self._get_connection()
        cur = conn.cursor()
        query = f'INSERT INTO {self.schema}.predicted_network' \
                '(designation, project_id) ' \
                'VALUES (%s, %s) ' \
                'RETURNING predicted_network_id;'
        params = (designation, project_id)
        cur.execute(query, params)
        predicted_network_id = next(iter(cur.fetchone()), None)
        conn.commit()
        self._put_connection(conn)
        if predicted_network_id is not None:
            self.set_predicted_network_of_project(
                project_id, predicted_network_id)
        return predicted_network_id

    @exception_decorator
    def get_predicted_network_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['predicted_network_id', 'project_id']
        reference_id: value of the id
        """
        if id_type not in ['predicted_network_id', 'project_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = sql.SQL(
            "SELECT * FROM {}.predicted_network WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        record = cur.fetchone()
        self._put_connection(conn)
        if record is None:
            raise MissingDataError('Select statement returned None.')
        return record

    @exception_decorator
    def delete_predicted_network_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['predicted_network_id', 'project_id']
        reference_id: value of the id
        """
        if id_type not in ['predicted_network_id', 'project_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = conn.cursor()
        query = sql.SQL(
            "DELETE FROM {}.predicted_network WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        conn.commit()
        self._put_connection(conn)

    # ####################################
    # NETWORK_FEATURES                   #
    # ####################################
    @exception_decorator
    def add_selected_network_feature_to_project(
        self,
        designation: str,
        feature_type: str,
        parameters: dict,
        predicted_network_id: str
    ):
        conn = self._get_connection()
        cur = conn.cursor()
        query = f'INSERT INTO {self.schema}.selected_network_features '\
                '(designation, feature_type, parameters, predicted_network_id) ' \
                'VALUES (%s, %s, %s, %s);'
        params = (designation, feature_type, Json(parameters), predicted_network_id)
        cur.execute(query, params)
        conn.commit()
        self._put_connection(conn)

    @exception_decorator
    def get_selected_network_features_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['selected_feature_id', 'predicted_network_id']
        reference_id: value of the id
        """
        if id_type not in ['selected_feature_id', 'predicted_network_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = sql.SQL(
            "SELECT * FROM {}.selected_network_features WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        records = cur.fetchall()
        self._put_connection(conn)
        if records is None:
            raise MissingDataError('Select statement returned None.')
        return records

    @exception_decorator
    def delete_selected_network_features_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['selected_feature_id', 'predicted_network_id']
        reference_id: value of the id
        """
        if id_type not in ['selected_feature_id', 'predicted_network_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = conn.cursor()
        query = sql.SQL(
            "DELETE FROM {}.selected_network_features WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        conn.commit()
        self._put_connection(conn)

    @exception_decorator
    def get_standard_network_features(self):
        """
        Return value is static.
        """
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = f'SELECT * FROM {self.schema}.standard_network_features;'
        cur.execute(query)
        records = cur.fetchall()
        self._put_connection(conn)
        if records is None:
            raise MissingDataError('Select statement returned None.')
        return records

    # ####################################
    # PREDICTED_EDGES                    #
    # ####################################
    @exception_decorator
    def add_edge_to_predicted_network(self, edge, edge_color, predicted_network_id):
        """
        edge: tuple (source_node: uuid, target_node: uuid)
        edge_color: str with color code
        predicted_network_id: uuid
        """
        conn = self._get_connection()
        cur = conn.cursor()
        query = f'INSERT INTO {self.schema}.predicted_edges ' \
                '(source_node, target_node, edge_color, predicted_network_id) ' \
                'VALUES (%s, %s, %s, %s) ' \
                'RETURNING predicted_edge_id;'
        params = (*edge, edge_color, predicted_network_id)
        cur.execute(query, params)
        record = cur.fetchone()
        conn.commit()
        self._put_connection(conn)
        return next(iter(record))

    @exception_decorator
    def get_edges_of_predicted_network_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['predicted_edge_id', 'predicted_network_id', 'project_id']
        reference_id: value of the id
        """
        if id_type not in ['predicted_edge_id', 'predicted_network_id', 'project_id']:
            raise ValueError('Parameter id_type is not valid!')
        if id_type == 'project_id':
            reference_id = self.get_predicted_network_by_id('project_id', reference_id)
            id_type = 'predicted_network_id'
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = sql.SQL(
            "SELECT * FROM {}.predicted_edges WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        records = cur.fetchall()
        self._put_connection(conn)
        if records is None:
            raise MissingDataError('Select statement returned None.')
        return records

    @exception_decorator
    def delete_edges_of_predicted_network_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['predicted_edge_id', 'predicted_network_id', 'project_id']
        reference_id: value of the id
        """
        if id_type not in ['predicted_edge_id', 'predicted_network_id', 'project_id']:
            raise ValueError('Parameter id_type is not valid!')
        if id_type == 'project_id':
            reference_id = self.get_predicted_network_by_id('project_id', reference_id)
            id_type = 'predicted_network_id'
        conn = self._get_connection()
        cur = conn.cursor()
        query = sql.SQL(
            "DELETE FROM {}.predicted_edges WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        conn.commit()
        self._put_connection(conn)

    # ####################################
    # PREDICTED_EDGE_COMPONENTS          #
    # ####################################
    @exception_decorator
    def add_component_to_predicted_edge(self, edge, predicted, prediction_score, predicted_edge_id):
        """
        edge: tuple (source_node: uuid, target_node: uuid)
        predicted: bool
        predicted_edge_id: uuid
        """

        conn = self._get_connection()
        cur = conn.cursor()
        query = f'INSERT INTO {self.schema}.predicted_edge_components ' \
                '(source, target, predicted, prediction_score, predicted_edge_id) ' \
                'VALUES (%s, %s, %s, %s, %s) ' \
                'RETURNING edge_component_id;'
        params = (*edge, predicted, prediction_score, predicted_edge_id)
        cur.execute(query, params)
        record = cur.fetchone()
        conn.commit()
        self._put_connection(conn)
        return next(iter(record))

    @exception_decorator
    def get_components_of_predicted_edge_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['edge_component_id', 'predicted_edge_id']
        reference_id: value of the id
        """
        if id_type not in ['edge_component_id', 'predicted_edge_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = sql.SQL(
            "SELECT * FROM {}.predicted_edge_components WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        records = cur.fetchall()
        self._put_connection(conn)
        if records is None:
            raise MissingDataError('Select statement returned None.')
        return records

    @exception_decorator
    def delete_component_of_predicted_edge_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['edge_component_id', 'predicted_edge_id']
        reference_id: value of the id
        """
        if id_type not in ['edge_component_id', 'predicted_edge_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = conn.cursor()
        query = sql.SQL(
            "DELETE FROM {}.predicted_edge_components WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        conn.commit()
        self._put_connection(conn)

    # ####################################
    # APPLIED_METHODS                    #
    # ####################################
    @exception_decorator
    def add_applied_methods_to_predicted_edge_component(self, method_list, edge_component_id):
        """
        method_list: [(method_designation: str, method_components: dict)]
        edge_component_id: uuid
        """
        conn = self._get_connection()
        cur = conn.cursor()
        args_str = ','.join(
            cur.mogrify(
                "(%s, %s, %s)",
                (method_designation, method_components, edge_component_id)
            ).decode("utf-8")
            for method_designation, method_components in method_list)
        cur.execute(
            f'INSERT INTO {self.schema}.applied_methods '
            '(method_designation, method_components, edge_component_id) '
            f'VALUES {args_str} '
            'RETURNING applied_method_id;'
        )
        records = [next(iter(record))
                   for record in cur.fetchall() if len(record) > 0]
        conn.commit()
        self._put_connection(conn)
        return records

    @exception_decorator
    def get_applied_methods_of_predicted_edge_component_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['applied_method_id', 'edge_component_id']
        reference_id: value of the id
        """
        if id_type not in ['applied_method_id', 'edge_component_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = sql.SQL(
            "SELECT * FROM {}.applied_methods WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        records = cur.fetchall()
        self._put_connection(conn)
        if records is None:
            raise MissingDataError('Select statement returned None.')
        return records

    @exception_decorator
    def delete_applied_methods_of_predicted_edge_component_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['applied_method_id', 'edge_component_id']
        reference_id: value of the id
        """
        if id_type not in ['applied_method_id', 'edge_component_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = conn.cursor()
        query = sql.SQL(
            "DELETE FROM {}.applied_methods WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        conn.commit()
        self._put_connection(conn)

    # ####################################
    # LINKPREDICTION_STATUS              #
    # ####################################
    @exception_decorator
    def add_linkprediction_status(
        self,
        thread_id: int,
        current_step: int,
        max_steps: int,
        process_step: str,
        status_value: str,
        id_type: str,
        reference_id: str
    ):
        """
        thread_id: Id of the thread that is calling this method
        current_step: Current process step as number
        max_steps: Count of all steps
        process_step: Description of the current process step
        status_value: Status value of the current process step
        id_type: Possible values = ['project_id', 'predicted_network_id']
        reference_id: Value of the Id
        """
        if id_type not in ['project_id', 'predicted_network_id']:
            raise ValueError('Parameter id_type is not valid!')
        if id_type == 'project_id':
            predicted_network = self.get_predicted_network_by_id(id_type, reference_id)
            reference_id = predicted_network['predicted_network_id']
            id_type = 'predicted_network_id'
        conn = self._get_connection()
        cur = conn.cursor()
        query = f'INSERT INTO {self.schema}.prediction_status ' \
                '(thread_id, log_timestamp, current_step, max_steps, process_step, ' \
                'status_value, predicted_network_id) ' \
                'VALUES (%s, %s, %s, %s, %s, %s, %s) ' \
                'RETURNING status_id;'
        params = (thread_id, datetime.now(), current_step, max_steps,
                  process_step, status_value, reference_id)
        cur.execute(query, params)
        record = cur.fetchone()
        conn.commit()
        self._put_connection(conn)
        return next(iter(record), None)

    @exception_decorator
    def get_last_linkprediction_status_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['status_id', 'project_id', 'predicted_network_id']
        reference_id: value of the id
        """
        if id_type not in ['status_id', 'project_id', 'predicted_network_id']:
            raise ValueError('Parameter id_type is not valid!')
        if id_type == 'project_id':
            predicted_network = self.get_predicted_network_by_id(id_type, reference_id)
            reference_id = predicted_network['predicted_network_id']
            id_type = 'predicted_network_id'
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = sql.SQL(
            'SELECT * FROM {}.prediction_status WHERE {} = {} ' \
            'ORDER BY log_timestamp DESC LIMIT 1;'
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        records = cur.fetchone()
        self._put_connection(conn)
        if records is None:
            raise MissingDataError('Select statement returned None.')
        return records

    @exception_decorator
    def delete_linkprediction_status_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['status_id', 'project_id', 'predicted_network_id']
        reference_id: value of the id
        """
        if id_type not in ['status_id', 'project_id', 'predicted_network_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = conn.cursor()
        query = sql.SQL(
            "DELETE FROM {}.prediction_status WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        conn.commit()
        self._put_connection(conn)

    # ####################################
    # EVALUATION_RESULTS                 #
    # ####################################
    @exception_decorator
    def add_or_update_evaluation_result(self, project_id, result_data):
        """
        project_id: project id as uuid (str)
        result_data: result data either as JSON string or as python dict
        """
        conn = self._get_connection()
        cur = conn.cursor()
        if isinstance(result_data, dict):
            result_data = Json(result_data)
        if self._check_if_row_exists('evaluation_results', 'project_id', project_id) is True:
            query = f'UPDATE {self.schema}.evaluation_results ' \
                    'SET result_data = %s ' \
                    'WHERE project_id = %s ' \
                    'RETURNING result_id;'
            params = (result_data, project_id)
        else:
            query = f'INSERT INTO {self.schema}.evaluation_results '\
                    '(project_id, result_data) ' \
                    'VALUES (%s, %s) ' \
                    'RETURNING result_id;'
            params = (project_id, result_data)
        cur.execute(query, params)
        record = cur.fetchone()
        conn.commit()
        self._put_connection(conn)
        return next(iter(record), None)

    @exception_decorator
    def get_evaluation_result_by_id(self, id_type, reference_id: str):
        """
        id_type: possible values = ['result_id', 'project_id']
        reference_id: value of the id
        """
        if id_type not in ['result_id', 'project_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = sql.SQL(
            "SELECT * FROM {}.evaluation_results WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        record = cur.fetchone()
        self._put_connection(conn)
        if record is None:
            raise MissingDataError('Select statement returned None.')
        return record

    @exception_decorator
    def delete_evaluation_result_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['result_id', 'project_id']
        reference_id: value of the id
        """
        if id_type not in ['result_id', 'project_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = conn.cursor()
        query = sql.SQL(
            "DELETE FROM {}.evaluation_results WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        conn.commit()
        self._put_connection(conn)

    # ####################################
    # NODES                              #
    # ####################################
    @exception_decorator
    def add_node(self, node_network_id, designation, original_network_id):
        conn = self._get_connection()
        cur = conn.cursor()
        query = f'INSERT INTO {self.schema}.nodes '\
                '(node_network_id, designation, original_network_id) ' \
                'VALUES (%s, %s, %s) ' \
                'RETURNING node_id;'
        params = (node_network_id, designation, original_network_id)
        cur.execute(query, params)
        record = cur.fetchone()
        conn.commit()
        self._put_connection(conn)
        return next(iter(record), None)

    @exception_decorator
    def add_nodes(self, node_list: list, original_network_id: str, predicted_network_id: str):
        """
        node_list: [(node_network_id: int, designation: str)]
        original_network_id: uuid
        predicted_network_id: uuid
        """
        conn = self._get_connection()
        cur = conn.cursor()
        args_str = ','.join(
            cur.mogrify(
                "(%s, %s, %s, %s)",
                (node_network_id, designation, original_network_id, predicted_network_id)
            ).decode("utf-8")
            for node_network_id, designation in node_list)
        cur.execute(
            f'INSERT INTO {self.schema}.nodes '
            '(node_network_id, designation, original_network_id, predicted_network_id) '
            f'VALUES {args_str} '
            'RETURNING node_network_id, node_id;'
        )
        records = cur.fetchall()
        conn.commit()
        self._put_connection(conn)
        return records

    @exception_decorator
    def get_nodes_by_id(self, id_type, reference_id: str):
        """
        id_type: possible values = ['node_id', 'original_network_id', 'predicted_network_id', 'project_id']
        reference_id: value of the id
        """
        if id_type not in ['node_id', 'original_network_id', 'predicted_network_id', 'project_id']:
            raise ValueError('Parameter id_type is not valid!')
        if id_type == 'project_id':
            original_network = self.get_original_network_by_id(id_type, reference_id)
            id_type = 'original_network_id'
            reference_id = original_network['original_network_id']
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = sql.SQL(
            "SELECT * FROM {}.nodes WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        records = cur.fetchall()
        self._put_connection(conn)
        if records is None:
            raise MissingDataError('Select statement returned None.')
        return records

    @exception_decorator
    def delete_nodes_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['node_id', 'original_network_id']
        reference_id: value of the id
        """
        if id_type not in ['node_id', 'original_network_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = conn.cursor()
        query = sql.SQL(
            "DELETE FROM {}.nodes WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        conn.commit()
        self._put_connection(conn)

    @exception_decorator
    def add_node_attributes(self, attribute_list, node_id):
        """
        attribute_list: [(attribute_name: str, attribute_value: str)]
        node_id: uuid
        """
        conn = self._get_connection()
        cur = conn.cursor()
        args_str = ','.join(
            cur.mogrify(
                "(%s, %s, %s)",
                (attribute_name, attribute_value, node_id)
            ).decode("utf-8")
            for attribute_name, attribute_value in attribute_list)
        cur.execute(
            f'INSERT INTO {self.schema}.node_attributes '
            '(attribute_name, attribute_value, node_id) '
            f'VALUES {args_str} '
            'RETURNING node_attribute_id;'
        )
        records = [next(iter(record)) for record in cur.fetchall() if len(record) > 0]
        conn.commit()
        self._put_connection(conn)
        return records

    @exception_decorator
    def get_node_attributes_by_id(self, id_type: str, reference_id: str):
        """
        id_type: possible values = ['node_id', 'node_attribute_id']
        reference_id: value of the id
        """
        if id_type not in ['node_id', 'node_attribute_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = self._get_dict_cursor(conn)
        query = sql.SQL(
            "SELECT * FROM {}.node_attributes WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        records = cur.fetchall()
        self._put_connection(conn)
        if records is None:
            raise MissingDataError('Select statement returned None.')
        return records

    @exception_decorator
    def get_distinct_node_attributes_by_id(self, id_type: str, reference_id: str):
        """
        id_type: possible values = ['original_network_id', 'predicted_network_id', 'project_id']
        reference_id: value of the id
        """
        if id_type not in ['original_network_id', 'predicted_network_id', 'project_id']:
            raise ValueError('Parameter id_type is not valid!')
        if id_type == 'project_id':
            original_network = self.get_original_network_by_id(id_type, reference_id)
            reference_id = original_network['original_network_id']
            id_type = 'original_network_id'
        conn = self._get_connection()
        cur = conn.cursor()
        query = sql.SQL(
            f'SELECT attribute_name FROM {self.schema}.node_attributes attr '
            f'INNER JOIN {self.schema}.nodes nodes '
            'ON nodes.node_id=attr.node_id '
            'WHERE nodes.{} = {} '
            'GROUP BY attribute_name;'
        ).format(
            *map(sql.Identifier, (id_type,)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        records = cur.fetchall()
        self._put_connection(conn)
        if records is None:
            raise MissingDataError('Select statement returned None.')
        return [next(iter(record)) for record in records]

    @exception_decorator
    def delete_node_attributes_by_id(self, id_type, reference_id):
        """
        id_type: possible values = ['node_id', 'node_attribute_id']
        reference_id: value of the id
        """
        if id_type not in ['node_id', 'node_attribute_id']:
            raise ValueError('Parameter id_type is not valid!')
        conn = self._get_connection()
        cur = conn.cursor()
        query = sql.SQL(
            "DELETE FROM {}.node_attributes WHERE {} = {};"
        ).format(
            *map(sql.Identifier, (self.schema, id_type)),
            *map(sql.Literal, (reference_id,))
        )
        cur.execute(query)
        conn.commit()
        self._put_connection(conn)

    # ####################################
    # GENERIC_METHODS                    #
    # ####################################
    @exception_decorator
    def _check_if_row_exists(self, table: str, column: str, value: str) -> bool:
        """
        table: name of the database table in the stored schema
        column: name of the column to look for
        value: value of the column
        """
        conn = self._get_connection()
        cur = conn.cursor()
        query = sql.SQL(
            "SELECT EXISTS(SELECT 1 FROM {}.{} WHERE {} = {});"
        ).format(
            *map(sql.Identifier, (self.schema, table, column)),
            *map(sql.Literal, (value,))
        )
        cur.execute(query)
        record = cur.fetchone()
        self._put_connection(conn)
        return next(iter(record))
