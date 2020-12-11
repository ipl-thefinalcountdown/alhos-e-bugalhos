import validators

import alhos_e_bugalhos.connections


class ExampleBackend(alhos_e_bugalhos.connections.Backend):
    '''
    Example backend object
    '''

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port

    @property
    def type_name(self) -> str:
        return 'Example Backend'

    @property
    def settings(self) -> alhos_e_bugalhos.connections.SettingsDict:
        return {
            'Host': self._host,
            'Port': self._port,
        }

    def update_setting(self, name: str, value: str):
        print(name, name == 'Host')
        if name == 'Host':
            self._host = value
        elif name == 'Port':
            try:
                self._port = int(value)
            except ValueError:
                raise alhos_e_bugalhos.connections.SettingError('Invalid Port')
        else:
            raise KeyError(f'Invalid setting: {name}')


class ExampleFrontend(alhos_e_bugalhos.connections.Frontend):
    '''
    Example front object
    '''

    def __init__(self, url: str) -> None:
        self._url = url

    @property
    def type_name(self) -> str:
        return 'Example Frontend'

    @property
    def settings(self) -> alhos_e_bugalhos.connections.SettingsDict:
        return {
            'URL': self._url,
        }

    def update_setting(self, name: str, value: str):
        if name == 'URL':
            if not validators.url(value):
                raise alhos_e_bugalhos.connections.SettingError('Invalid URL')
            self._url = value
        else:
            raise KeyError(f'Invalid setting: {name}')
