# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from linkprediction.openapi_server.models.base_model_ import Model
from linkprediction.openapi_server import util


class Predictor(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, designation=None, category=None, parameters=None):  # noqa: E501
        """Predictor - a model defined in OpenAPI

        :param id: The id of this Predictor.  # noqa: E501
        :type id: str
        :param designation: The designation of this Predictor.  # noqa: E501
        :type designation: str
        :param category: The category of this Predictor.  # noqa: E501
        :type category: str
        :param parameters: The parameters of this Predictor.  # noqa: E501
        :type parameters: object
        """
        self.openapi_types = {
            'id': str,
            'designation': str,
            'category': str,
            'parameters': object
        }

        self.attribute_map = {
            'id': 'id',
            'designation': 'designation',
            'category': 'category',
            'parameters': 'parameters'
        }

        self._id = id
        self._designation = designation
        self._category = category
        self._parameters = parameters

    @classmethod
    def from_dict(cls, dikt) -> 'Predictor':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Predictor of this Predictor.  # noqa: E501
        :rtype: Predictor
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this Predictor.


        :return: The id of this Predictor.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Predictor.


        :param id: The id of this Predictor.
        :type id: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def designation(self):
        """Gets the designation of this Predictor.


        :return: The designation of this Predictor.
        :rtype: str
        """
        return self._designation

    @designation.setter
    def designation(self, designation):
        """Sets the designation of this Predictor.


        :param designation: The designation of this Predictor.
        :type designation: str
        """
        if designation is None:
            raise ValueError("Invalid value for `designation`, must not be `None`")  # noqa: E501

        self._designation = designation

    @property
    def category(self):
        """Gets the category of this Predictor.


        :return: The category of this Predictor.
        :rtype: str
        """
        return self._category

    @category.setter
    def category(self, category):
        """Sets the category of this Predictor.


        :param category: The category of this Predictor.
        :type category: str
        """
        if category is None:
            raise ValueError("Invalid value for `category`, must not be `None`")  # noqa: E501

        self._category = category

    @property
    def parameters(self):
        """Gets the parameters of this Predictor.


        :return: The parameters of this Predictor.
        :rtype: object
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """Sets the parameters of this Predictor.


        :param parameters: The parameters of this Predictor.
        :type parameters: object
        """
        if parameters is None:
            raise ValueError("Invalid value for `parameters`, must not be `None`")  # noqa: E501

        self._parameters = parameters
