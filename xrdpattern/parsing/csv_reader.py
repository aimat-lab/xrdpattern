from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from xrdpattern.pattern import XAxisType
# -------------------------------------------

class Orientation(Enum):
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'


@dataclass
class CsvScheme:
    variable_type : XAxisType
    pattern_dimension : Orientation
    header_lines : int = 1


class NumericalTable(list[list[str]]):
    def get_header(self):
        return self[0]

    def get_data(self, index: int) -> list[float]:
        if index == 0:
            raise ValueError("Index 0 is reserved for the header")
        row = self[index]

        err = None
        numerical_data = []
        for entry in row:
            try:
                value = float(entry)
                numerical_data.append(value)
            except BaseException as e:
                err = TypeError(f'Failed to convert value \"{entry}\" to value on table row \"{index}\": {str(e)}')
                break
        if err:
            raise err

        return numerical_data


class CsvPreprocessor:
    def __init__(self, seperator : str):
        if not seperator in [',', ';', '\t']:
            raise ValueError(f"Invalid seperator: {seperator}")
        self.seperator : str = seperator


    def generate_xy_files(self, csv_fpath : str, csv_scheme : CsvScheme):
        table = self.read_csv(file_path=)


    def read_csv(self, file_path: str, outerDimensionAxis: Orientation) -> NumericalTable:
        data = []
        with open(file_path, 'r', newline='') as infile:
            for line in infile:
                row = line.strip().split(self.seperator)
                data.append(row)

        if outerDimensionAxis == Orientation.HORIZONTAL:
            data = [list(col) for col in zip(*data)]
        return NumericalTable(data)

