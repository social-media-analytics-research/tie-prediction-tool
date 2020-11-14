# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.project import Project  # noqa: E501
from openapi_server.test import BaseTestCase


class TestProjectsController(BaseTestCase):
    """ProjectsController integration test stubs"""

    @unittest.skip("multipart/form-data not supported by Connexion")
    def test_create_project(self):
        """Test case for create_project

        Creates a project with an original network file.
        """
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'multipart/form-data',
        }
        data = dict(designation='designation_example',
                    description='description_example',
                    network_designation='network_designation_example',
                    network_directed=True,
                    network_multigraph=True,
                    network_file=(BytesIO(b'some file data'), 'file.txt'),
                    file_format='file_format_example')
        response = self.client.open(
            '/api/projects',
            method='POST',
            headers=headers,
            data=data,
            content_type='multipart/form-data')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_project_by_id(self):
        """Test case for delete_project_by_id

        Delete project by an ID.
        """
        headers = { 
        }
        response = self.client.open(
            '/api/projects/{project_id}'.format(project_id=046b6c7f-0b8a-43b9-b35d-6489e6daee91),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_project_by_id(self):
        """Test case for get_project_by_id

        Find project by an ID.
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/projects/{project_id}'.format(project_id=046b6c7f-0b8a-43b9-b35d-6489e6daee91),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_projects(self):
        """Test case for get_projects

        Returns a list of available projects.
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/projects',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @unittest.skip("multipart/form-data not supported by Connexion")
    def test_update_project_by_id(self):
        """Test case for update_project_by_id

        Update project by an ID.
        """
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'multipart/form-data',
        }
        data = dict(designation='designation_example',
                    description='description_example',
                    network_designation='network_designation_example',
                    network_directed=True,
                    network_multigraph=True,
                    network_file=(BytesIO(b'some file data'), 'file.txt'),
                    file_format='file_format_example')
        response = self.client.open(
            '/api/projects/{project_id}'.format(project_id=046b6c7f-0b8a-43b9-b35d-6489e6daee91),
            method='PUT',
            headers=headers,
            data=data,
            content_type='multipart/form-data')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
