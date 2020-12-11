import abc

from typing import Dict, Union


SettingsDict = Dict[str, Union[str, int]]


class SettingError(Exception):
    pass


class Provider(abc.ABC):
    @property
    @abc.abstractmethod
    def type_name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def settings(self) -> SettingsDict:
        pass

    @abc.abstractmethod
    def update_setting(self, name: str, value: str) -> SettingsDict:
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
