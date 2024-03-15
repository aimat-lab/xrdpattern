from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .table_selector import TableSelector, NumericalTable, TextTable
from xrdpattern.pattern import XAxisType
# -------------------------------------------

class Orientation(Enum):
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'


@dataclass
class CsvScheme:
    x_axis_type : XAxisType
    pattern_dimension : Orientation
    header_lines : int = 1


class CsvPreprocessor:
    def __init__(self, seperator : str):
        if not seperator in [',', ';', '\t']:
            raise ValueError(f"Invalid seperator: {seperator}")
        self.seperator : str = seperator


    def read_csv(self, fpath: str, outerDimensionAxis: Orientation = Orientation.VERTICAL) -> NumericalTable:
        data = []
        with open(fpath, 'r', newline='') as infile:
            for line in infile:
                row = [item.strip() for item in line.strip().split(self.seperator)]
                if row and any(item for item in row):
                    data.append(row)

        if outerDimensionAxis == Orientation.HORIZONTAL:
            data = [list(col) for col in zip(*data)]
        table = TextTable(data)
        print(f'fpath,row, col length = {fpath} {table.get_row_count()}, {table.get_row_len()}')
        return TableSelector.get_numerical_subtable(table=table)

