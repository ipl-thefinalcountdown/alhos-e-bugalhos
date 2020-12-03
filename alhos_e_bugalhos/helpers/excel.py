from typing import Any, Dict, List

import xlrd


class ExcelHelper:
    def __init__(self, input: str):
        self.workbook = xlrd.open_workbook(input)

    def to_json(self) -> Dict[Any, Any]:
        dict_ret: List[Dict[Any, Any]] = []
        sheets = self.workbook.sheet_names()
        for sheet in sheets:
            worksheet = self.workbook.sheet_by_name(sheet)
            dict_ret.append(self._to_json_worksheet(worksheet))

        return dict_ret

    @staticmethod
    def _to_json_worksheet(worksheet: xlrd.sheet.Sheet) -> Dict[Any, Any]:
        dict_list: List[Dict[Any, Any]] = []
        header: List[str] = [cell.value for cell in worksheet.row(0)]

        for row_idx in range(1, worksheet.nrows):
            row_dict = {
                header[col_idx]: cell.value
                for col_idx, cell in enumerate(worksheet.row(row_idx))
            }
            dict_list.append(row_dict)

        return dict_list
