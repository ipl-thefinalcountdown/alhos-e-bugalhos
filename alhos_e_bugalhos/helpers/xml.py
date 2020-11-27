import json

from typing import Any, Dict

import xmltodict

from jsonhelper import JsonHelper


class XMLHelper:
    """Converts a XML string to other formats"""

    @staticmethod
    def to_json(input: str) -> Dict[Any, Any]:
        """Converts to a JSON Object

        Params: `input` = XML string to convert

        Returns: a JSON Object with the input's data
        """
        return json.dumps(xmltodict.parse(input))

    @classmethod
    def to_html_table(cls, input: str) -> str:
        """Converts to an HTML Table string

        Params: `input` = XML string to convert

        Returns: an HTML table string with the input's data
        """
        return JsonHelper.to_html_table(cls.to_json(input))
