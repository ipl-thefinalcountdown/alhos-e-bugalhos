import csv
import io
import json
import xml.etree.ElementTree as ET

from typing import Any

import requests
import validators
import xmltodict
import yaml

import alhos_e_bugalhos.connections


class XMLBackend(alhos_e_bugalhos.connections.Backend):
    TYPE_NAME = 'XML'
    SETTINGS = [
        'Data',
    ]

    def validate_setting(self, name: str, value: Any):
        if name == 'Data':
            if not value:
                raise alhos_e_bugalhos.connections.SettingError('Invalid Data')
            try:
                ET.fromstring(value)
            except ET.ParseError:
                raise alhos_e_bugalhos.connections.SettingError('Invalid Data')
            return value

    def get_data(self, params=None):
        return xmltodict.parse(self.settings['Data'])


class CSVBackend(alhos_e_bugalhos.connections.Backend):
    TYPE_NAME = 'CSV'
    SETTINGS = [
        'Data',
    ]

    def validate_setting(self, name: str, value: Any):
        if name == 'Data':
            if not value:
                raise alhos_e_bugalhos.connections.SettingError('Invalid Data')
            try:
                csv.DictReader(io.StringIO(value))
            except (ValueError, csv.Error):
                raise alhos_e_bugalhos.connections.SettingError('Invalid Data')
            return value

    def get_data(self, params=None):
        return dict(csv.DictReader(io.StringIO(self.settings['Data'])))


class JSONBackend(alhos_e_bugalhos.connections.Backend):
    TYPE_NAME = 'JSON'
    SETTINGS = [
        'Data',
    ]

    def validate_setting(self, name: str, value: Any):
        if name == 'Data':
            try:
                json.loads(value)
            except json.JSONDecodeError:
                raise alhos_e_bugalhos.connections.SettingError('Invalid Data')
            return value

    def get_data(self, params=None):
        return json.loads(self.settings['Data'])


class YAMLBackend(alhos_e_bugalhos.connections.Backend):
    TYPE_NAME = 'YAML'
    SETTINGS = [
        'Data',
    ]

    def validate_setting(self, name: str, value: Any):
        if name == 'Data':
            try:
                dict(yaml.load(value))
            except (TypeError, ValueError, yaml.YAMLError):
                raise alhos_e_bugalhos.connections.SettingError('Invalid Data')
            return value

    def get_data(self, params=None):
        return dict(yaml.load(self.settings['Data']))


class RESTBackend(alhos_e_bugalhos.connections.Backend):
    TYPE_NAME = 'REST'
    SETTINGS = [
        'URL',
        'Type',
    ]

    @staticmethod
    def get_callback(name: str):
        if name == 'GET':
            return requests.get
        elif name == 'POST':
            return requests.post
        elif name == 'PUT':
            return requests.put
        elif name == 'PATCH':
            return requests.patch
        elif name == 'DELETE':
            return requests.delete

    def validate_setting(self, name: str, value: Any):
        if name == 'URL':
            value = str(value)
            if not validators.url(value):
                raise alhos_e_bugalhos.connections.SettingError('Invalid URL')
            return value
        if name == 'Type':
            value = value.upper()
            if self.get_callback(value):
                return value
            else:
                raise alhos_e_bugalhos.connections.SettingError('Invalid REST request type')

    def get_data(self, params=None):
        response = self.get_callback(self.settings['Type'])(self.settings['URL'])
        return {
            'status': response.status_code,
            'data': response.json(),
        }
