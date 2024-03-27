from __future__ import annotations
from dataclasses import dataclass
from hollarek.abstract import SelectableEnum
from xrdpattern.pattern import XAxisType, XrdPattern
from .table_selector import TableSelector, NumericalTable, TextTable

# -------------------------------------------

class Orientation(SelectableEnum):
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'


class Seperator(SelectableEnum):
    COMMA = ','
    SEMICOLON = ';'
    TAB = '\t'


@dataclass
class CsvScheme:
    x_axis_type : XAxisType
    pattern_dimension : Orientation
    seperator: str = ','
    header_lines : int = 1

    def __post_init__(self):
        if not self.seperator in [',', ';', '\t']:
            raise ValueError(f"Invalid seperator: {self.seperator}")

    @classmethod
    def from_manual(cls) -> CsvScheme:
        print(f'Please specify csv scheme')
        x_axis_type = XAxisType.from_manual_query()
        pattern_dimension = Orientation.from_manual_query()
        seperator = Seperator.from_manual_query()
        return CsvScheme(x_axis_type=x_axis_type, pattern_dimension=pattern_dimension, seperator=seperator)


class CsvReader:
    def __init__(self, csv_scheme : CsvScheme):
        self.csv_scheme : CsvScheme = csv_scheme


    def read_csv(self, fpath: str) -> XrdPattern:
        data = []
        with open(fpath, 'r', newline='') as infile:
            for line in infile:
                row = [item.strip() for item in line.strip().split(self.csv_scheme.seperator)]
                if row and any(item for item in row):
                    data.append(row)

        if self.csv_scheme.pattern_dimension == Orientation.HORIZONTAL:
            data = [list(col) for col in zip(*data)]
        table = TextTable(data)
        print(f'fpath,row, col length = {fpath} {table.get_row_count()}, {table.get_row_len()}')
        # return TableSelector.get_numerical_subtable(table=table)

