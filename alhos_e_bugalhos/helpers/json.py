from typing import Any, Dict

import xmltodict

from json2html import json2html


class JsonHelper:
    """Converts a JSON Object to other formats"""

    @staticmethod
    def to_html_table(input: Dict[Any, Any]) -> str:
        """Converts to an HTML table

        Params: `input` = JSON Object to convert

        Returns: an HTML table string with the input's data
        """
        return json2html.convert(json=input)

    @staticmethod
    def to_xml(input: Dict[Any, Any]) -> str:
        """Converts to XML

        Params: `input` = JSON Object to convert

        Returns: a XML string with the input's data
        """
        return xmltodict.unparse(input)
