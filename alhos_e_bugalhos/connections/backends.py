import xml.etree.ElementTree as ET

from typing import Any

import xmltodict

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
