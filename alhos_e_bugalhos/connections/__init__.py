import abc

from typing import Any, ClassVar, Dict, List, Optional, Union


SettingValues = Union[str, int]
SettingsDict = Dict[str, SettingValues]


class ProviderError(Exception):
    pass


class SettingError(ProviderError):
    pass


class Provider(abc.ABC):
    TYPE_NAME: ClassVar[Optional[str]]
    SETTINGS: ClassVar[Optional[List[str]]] = None

    def __init__(self, settings) -> None:
        if not self.TYPE_NAME:
            raise Provider(
                f'Error when instantiating {self.__class__.__name__} class: '
                'missing TYPE_NAME attribute'
            )

        for setting_name in self.SETTINGS:
            if ' ' in setting_name:
                raise SettingError(
                    f"Invalid setting name, setting names can't contain spaces: {setting_name}"
                )
            if setting_name not in settings:
                raise SettingError(f'Missing setting value: {setting_name}')

        self._settings = {}

        for name, value in settings.items():
            if name not in self.SETTINGS:
                raise SettingError(f'Unknown setting: {name}')
            self.update_setting(name, value)

    def update_setting(self, name: str, value: Any):
        if name not in self.SETTINGS:
            raise KeyError(f'Invalid setting: {name}')
        self._settings[name] = self.validate_setting(name, value)

    @property
    def settings(self) -> SettingsDict:
        return self._settings

    @property
    def available_settings(self) -> List[str]:
        return self.SETTINGS

    @abc.abstractmethod
    def validate_setting(self, name: str, value: Any) -> Optional[SettingValues]:
        '''
        Validates a setting value and returns the internal interpretation for it
        '''
        pass


class Backend(Provider):
    pass


class Frontend(Provider):
    pass


class Connection():
    def __init__(self, name: str, input_: Frontend, output: Backend) -> None:
        self._name = name
        self._input = input_
        self._output = output

    @property
    def name(self) -> str:
        return self._name

    @property
    def input(self) -> Frontend:
        return self._input

    @property
    def output(self) -> Backend:
        return self._output
