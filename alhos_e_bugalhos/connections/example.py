from typing import Any

import validators

import alhos_e_bugalhos.connections


class ExampleBackend(alhos_e_bugalhos.connections.Backend):
    '''
    Example backend object
    '''
    TYPE_NAME = 'Example Backend'
    SETTINGS = [
        'Host',
        'Port',
    ]

    def validate_setting(self, name: str, value: Any):
        if name == 'Host':
            return str(value)
        elif name == 'Port':
            try:
                return int(value)
            except ValueError:
                raise alhos_e_bugalhos.connections.SettingError('Invalid Port')


class ExampleFrontend(alhos_e_bugalhos.connections.Frontend):
    '''
    Example front object
    '''
    TYPE_NAME = 'Example Frontend'
    SETTINGS = [
        'URL',
    ]

    def validate_setting(self, name: str, value: Any):
        if name == 'URL':
            value = str(value)
            if not validators.url(value):
                raise alhos_e_bugalhos.connections.SettingError('Invalid URL')
            return value
