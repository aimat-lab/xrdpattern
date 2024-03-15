from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from xrdpattern.parsing.csv.table_selector import Index

# -------------------------------------------

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


    # -------------------------------------------
    # get rows/cols

    def get_row(self, row : int, start_col : int = 0, end_col : Optional[int] = None):
        end_col = end_col if not end_col is None else self.get_row_len()-1
        return [self.content[row][col] for col in range(start_col, end_col+1)]


    def get_col(self, col : int, start_row : int = 0, end_row : Optional[int]  = None):
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

