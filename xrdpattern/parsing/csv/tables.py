from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
# -------------------------------------------
@dataclass
class Index:
    row : int
    col : int

    def __eq__(self, other):
        if not isinstance(other, Index):
            return False
        return self.row == other.row and self.col == other.col

@dataclass
class Region:
    upper_left: Index
    lower_right: Index

    def __eq__(self, other):
        if not isinstance(other, Region):
            return False
        return self.upper_left == other.upper_left and self.lower_right == other.lower_right

    def get_horizontal_length(self) -> int:
        return self.lower_right.col - self.upper_left.col + 1

    def get_vertical_length(self) -> int:
        return self.lower_right.row - self.upper_left.row + 1

    def get_horizontal_indices(self):
        return range(self.upper_left.col, self.lower_right.col+1)

    def get_vertical_indices(self):
        return range(self.upper_left.row, self.lower_right.row+1)

@dataclass
class TextTable:
    content: list[list[str]]

    def __post_init__(self):
        max_length = max(len(row) for row in self.content)
        for i, row in enumerate(self.content):
            additional_length = max_length - len(row)
            if additional_length > 0:
                self.content[i] += [''] * additional_length

        if not all([len(row) == len(self.content[0]) for row in self.content]):
            raise ValueError("All rows must have the same length")


    def get_lower_right_index(self) -> Index:
        return Index(self.get_row_count() - 1, self.get_row_len() - 1)

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
        if not len(self.headers) == len(self.data[0]):
            raise ValueError(f"Number of headers ({len(self.headers)}) does not match number"
                             f" of data columns ({len(self.data)})")

    def get_data(self, row : int) -> list[float]:
        return self.data[row]

    def get_headers(self, row : int) -> str:
        return self.headers[row]


    def get_row_count(self) -> int:
        return len(self.data)
