from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .table_selector import TableSelector
# -------------------------------------------
@dataclass
class Index:
    row : int
    col : int

@dataclass
class Region:
    upper_left: Index
    lower_right: Index

    def get_horizontal_length(self) -> int:
        return self.lower_right.col - self.upper_left.col + 1

    def get_vertical_length(self) -> int:
        return self.lower_right.row - self.upper_left.row + 1


@dataclass
class TextTable:
    content: list[list[str]]

    def __getitem__(self, item):
        return self.content[item]

    def __post_init__(self):
        if not all([len(row) == len(self.content[0]) for row in self.content]):
            raise ValueError("All rows must have the same length")

    def get_lower_right_index(self) -> Index:
        return Index(self.get_row_count() - 1, self.get_row_len() - 1)

    def get_numerical_subtable(self) -> NumericalTable:
        selector = TableSelector(table=self, discriminator=is_numeric)
        data_region = selector.get_lower_right_region()

        if not data_region:
            raise ValueError("No numerical data found")

        data =  self.get_subtable(region=data_region, dtype=float)
        preamble = ''
        headers = ['' for _ in range(data_region.get_horizontal_length())]
        for row_num in range(data_region.upper_left.row):
            row = self.get_row(row_num)
            preamble += ''.join(row)
            headers += row[data_region.upper_left.row:]

        return NumericalTable(preable=preamble, headers=headers, data=data)

    # -------------------------------------------
    # get rows/cols

    def get_subtable(self, region : Region, dtype : type):
        subtable = []
        for row in range(region.upper_left.row, region.lower_right.row+1):
            row = self.get_row(row=row, start_col=region.upper_left.col, end_col=region.lower_right.col)
            data_row = [dtype(x) for x in row]
            subtable.append(data_row)
        return subtable

    def get_row(self, row : int, start_col : int = 0, end_col : Optional[int] = None) -> list[str]:
        end_col = end_col if not end_col is None else self.get_row_len()-1
        return [self.content[row][col] for col in range(start_col, end_col+1)]

    def get_col(self, col : int, start_row : int = 0, end_row : Optional[int]  = None) -> list[str]:
        end_row = end_row if not end_row is None else self.get_row_count()-1
        return [self.content[row][col] for row in range(start_row, end_row+1)]

    def get_row_count(self) -> int:
        return len(self.content)

    def get_row_len(self) -> int:
        return len(self.content[0])




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


def is_numeric(text : str) -> boolg:
    try:
        float(text)
        return True
    except:
        return False
