# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.evaluation_results import EvaluationResults  # noqa: E501
from openapi_server.models.prediction_setup import PredictionSetup  # noqa: E501
from openapi_server.models.prediction_state import PredictionState  # noqa: E501
from openapi_server.models.prediction_status import PredictionStatus  # noqa: E501
from openapi_server.models.predictors import Predictors  # noqa: E501
from openapi_server.test import BaseTestCase


class TestPredictionController(BaseTestCase):
    """PredictionController integration test stubs"""

    def test_create_prediction_setup(self):
        """Test case for create_prediction_setup

        Creates a prediction.
        """
        prediction_setup = {
  "selected_predictors" : [ {
    "id" : "046b6c7f-0b8a-43b9-b35d-6489e6daee91",
    "designation" : "Jaccard",
    "category" : "Topology"
  }, {
    "id" : "046b6c7f-0b8a-43b9-b35d-6489e6daee91",
    "designation" : "Jaccard",
    "category" : "Topology"
  } ],
  "evaluation_setup" : {
    "random_seed" : 42,
    "with_validation" : true,
    "train_sampling_ratio" : 0.7,
    "test_sampling_ratio" : 0.9
  }
}
        headers = { 
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/projects/{project_id}/prediction/predictors'.format(project_id=046b6c7f-0b8a-43b9-b35d-6489e6daee91),
            method='POST',
            headers=headers,
            data=json.dumps(prediction_setup),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_prediction_setup(self):
        """Test case for delete_prediction_setup

        Delete selected prediction setup of a project.
        """
        headers = { 
        }
        response = self.client.open(
            '/api/projects/{project_id}/prediction/predictors'.format(project_id=046b6c7f-0b8a-43b9-b35d-6489e6daee91),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_evaluation_results_by_project(self):
        """Test case for get_evaluation_results_by_project

        Find evaluation results by project ID.
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/projects/{project_id}/prediction/evaluation'.format(project_id=046b6c7f-0b8a-43b9-b35d-6489e6daee91),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_prediction_status_by_project(self):
        """Test case for get_prediction_status_by_project

        Find prediction status by a project ID.
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/projects/{project_id}/prediction'.format(project_id=046b6c7f-0b8a-43b9-b35d-6489e6daee91),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_predictors_by_project(self):
        """Test case for get_predictors_by_project

        Find predictors by project ID.
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/projects/{project_id}/prediction/predictors'.format(project_id=046b6c7f-0b8a-43b9-b35d-6489e6daee91),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_handle_prediction_state_by_project(self):
        """Test case for handle_prediction_state_by_project

        Handles the state of the prediction of a project.
        """
        prediction_state = {
  "state" : "Start"
}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/projects/{project_id}/prediction'.format(project_id=046b6c7f-0b8a-43b9-b35d-6489e6daee91),
            method='PUT',
            headers=headers,
            data=json.dumps(prediction_state),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
