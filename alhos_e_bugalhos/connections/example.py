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
