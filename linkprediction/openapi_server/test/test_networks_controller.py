# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.original_network import OriginalNetwork  # noqa: E501
from openapi_server.models.predicted_network import PredictedNetwork  # noqa: E501
from openapi_server.test import BaseTestCase


class TestNetworksController(BaseTestCase):
    """NetworksController integration test stubs"""

    def test_delete_original_network_by_project(self):
        """Test case for delete_original_network_by_project

        Delete original network by a project ID.
        """
        headers = { 
        }
        response = self.client.open(
            '/api/projects/{project_id}/originalnetwork'.format(project_id=046b6c7f-0b8a-43b9-b35d-6489e6daee91),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_predicted_network_by_project(self):
        """Test case for delete_predicted_network_by_project

        Delete predicted network of by a project ID.
        """
        headers = { 
        }
        response = self.client.open(
            '/api/projects/{project_id}/predictednetwork'.format(project_id=046b6c7f-0b8a-43b9-b35d-6489e6daee91),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_original_network_by_project(self):
        """Test case for get_original_network_by_project

        Find original network by a project ID.
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/projects/{project_id}/originalnetwork'.format(project_id=046b6c7f-0b8a-43b9-b35d-6489e6daee91),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_predicted_network_by_project(self):
        """Test case for get_predicted_network_by_project

        Find predicted network by a project ID.
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/projects/{project_id}/predictednetwork'.format(project_id=046b6c7f-0b8a-43b9-b35d-6489e6daee91),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
