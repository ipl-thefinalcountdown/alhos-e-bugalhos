from __future__ import annotations

import abc

from typing import Any, Callable, ClassVar, Dict, List, Optional, Union


SettingValues = Union[str, int]
SettingsDict = Dict[str, SettingValues]


class ProviderError(Exception):
    pass


class SettingError(ProviderError):
    pass


class MultipleSettingError(ProviderError):
    def __init__(self, errors: Dict[str, str]):
        super().__init__(f'Invalid settings: {", ".join(errors)}')
        self._errors = errors

    @property
    def errors(self) -> Dict[str, str]:
        return self._errors  # setting name, error description


class Provider(abc.ABC):
    TYPE_NAME: ClassVar[Optional[str]]
    SETTINGS: ClassVar[Optional[List[str]]] = None
    TEXT_SETTINGS: ClassVar[Optional[List[str]]] = None

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

        errors = {}
        for name, value in settings.items():
            if name not in self.SETTINGS:
                raise SettingError(f'Unknown setting: {name}')
            try:
                self.update_setting(name, value)
            except SettingError as e:
                errors[name] = e.args[0]

        if errors:
            raise MultipleSettingError(errors)

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

    def validate_setting(self, name: str, value: Any) -> Optional[SettingValues]:
        '''
        Validates a setting value and returns the internal interpretation for it
        '''
        pass


class Backend(Provider):
    @abc.abstractmethod
    def get_data(self, params: Optional[Dict[str, str]] = None) -> Dict[Any, Any]:
        pass


BackendGetData = Callable[[Optional[Dict[str, str]]], Dict[Any, Any]]


class Frontend(Provider):
    @abc.abstractmethod
    def register(self, get_data: BackendGetData):
        pass

    def unregister(self):
        pass


class Connection():
    def __init__(self, name: str, input_: Frontend, output: Backend) -> None:
        self._name = name
        self._input = input_
        self._output = output

        self.output.register(self.input.get_data)

    def __del__(self):
        self.output.unregister()

    @property
    def name(self) -> str:
        return self._name

    @property
    def input(self) -> Frontend:
        return self._input

    @property
    def output(self) -> Backend:
        return self._output
