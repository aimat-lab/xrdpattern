from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable
from xrdpattern.pattern import XAxisType, IntensityMap
# -------------------------------------------

class Orientation(Enum):
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'


@dataclass
class CsvScheme:
    x_axis_type : XAxisType
    pattern_dimension : Orientation
    header_lines : int = 1


@dataclass
class Region:
    x_start : int
    y_start : int
    y_end : int
    x_end : int

class TextTable(list[list[str]]):
    def get_maximal_region(self, discriminator: Callable[[str], bool]) -> Region:
        max_region = Region(0, 0, 0, 0)
        remaining_indices = {(x, y) for x in range(len(self)) for y in range(len(self[0]))}

        while remaining_indices:
            x_start, y_start = remaining_indices.pop()

            if not discriminator(self[x_start][y_start]):
                continue

            x_end, y_end = x_start, y_start



            # Update maximal region if necessary
            if (x_end - x_start + 1) * (y_end - y_start + 1) > (max_region.x_end - max_region.x_start + 1)


    def get_maximal_expansion(self, x_start : int, y_start, discriminator : Callable[[str], bool]) -> Region:
        x_end, y_end = x_start+1, y_start+1
        while y_end + 1 < len(self[0]):
            delta = self[x_start:x_end][y_start:y_start+1]
            is_ok = all(discriminator for x in delta)
            if not is_ok:
                break
            y_end += 1

        while x_end + 1 < len(self):
            delta = self[x_start:x_start+1][y_start:y_end]
            is_ok = all(discriminator for x in delta)
            if not is_ok:
                break
            x_end += 1
        return Region(x_start=x_start, y_start=y_start, x_end=x_end, y_end=y_end)




@dataclass
class NumericalTable:
    preable : str
    headers : list[str]
    data : list[list[float]]

    def __post_init__(self):
        if not len(self.headers) == len(self.data):
            raise ValueError(f"Number of headers ({len(self.headers)}) does not match number"
                             f" of data columns ({len(self.data)})")


    def get_data(self, index : int) -> list[float]:
        return self.data[index]

    def get_header(self, index : int) -> str:
        return self.headers[index]





class CsvPreprocessor:
    def __init__(self, seperator : str):
        if not seperator in [',', ';', '\t']:
            raise ValueError(f"Invalid seperator: {seperator}")
        self.seperator : str = seperator


    def generate_xy_files(self, csv_fpath : str, csv_scheme : CsvScheme):
        numerical_table = self.read_csv(file_path=csv_fpath,outerDimensionAxis=csv_scheme.pattern_dimension)
        for index in range(len(numerical_table)):
            try:
                x_values = numerical_table.get_first_data_row()
                intensities = numerical_table.get_data(index=index)
                data = {}
                for x,y in zip(x_values, intensities):
                    data[x] = y
                map = IntensityMap(data=data, x_axis_type=csv_scheme.x_axis_type)
            except:
                pass



    def read_csv(self, file_path: str, outerDimensionAxis: Orientation) -> NumericalTable:
        data = []
        with open(file_path, 'r', newline='') as infile:
            for line in infile:
                row = line.strip().split(self.seperator)
                data.append(row)

        if outerDimensionAxis == Orientation.HORIZONTAL:
            data = [list(col) for col in zip(*data)]
        return NumericalTable(data)



    # def get_preable(self) -> list[list[str]]:
    #     return self[:self.locate_data_start()]
    #
    # def get_first_data_row(self) -> list[float]:
    #     return self.get_data(index=self.locate_data_start())
    #
    # def locate_data_start(self) -> int:
    #     for index in range(len(self)):
    #         try:
    #             self.get_data(index=index)
    #             return index
    #         except:
    #             pass
    #     raise ValueError(f'Failed to locate start of numerical data. Is this a numerical table?')
    #
    # def get_data(self, index: int) -> list[float]:
    #     err = None
    #     numerical_data = []
    #     for entry in self[index]:
    #         try:
    #             value = float(entry)
    #             numerical_data.append(value)
    #         except BaseException as e:
    #             err = TypeError(f'Failed to convert value \"{entry}\" to value on table row \"{index}\": {str(e)}')
    #             break
    #     if err:
    #         raise err
    #
    #     return numerical_data

