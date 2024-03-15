from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class Index:
    row : int
    col : int


@dataclass
class Region:
    upper_left : Index
    lower_right : Index


@dataclass
class TextTable:
    content: list[list[str]]

    def __getitem__(self, item):
        return self.content[item]

    def __post_init__(self):
        if not all([len(row) == len(self.content[0]) for row in self.content]):
            raise ValueError("All rows must have the same length")

    def get_lower_right_subtable(self, discriminator : Callable[[str], bool]) -> Region:
        upper_left = None
        new_upper_left = self.get_lower_right_index()
        while True:
            partial_row = self.get_row(new_upper_left.row, new_upper_left.col)
            failed_on_row = not all([discriminator(x) for x in partial_row])

            partial_col = self.get_col(new_upper_left.col, new_upper_left.row)
            failed_on_col = not all([discriminator(x) for x in partial_col])
            if not failed_on_row and not failed_on_col:
                upper_left = Index(row=new_upper_left.row,col=new_upper_left.col)
                new_upper_left.row -= 1
                new_upper_left.col -= 1
            else:
                break

        while True:
            partial_col = self.get_col(col=upper_left.col-1, start_row=upper_left.row)
            is_ok = all([discriminator(x) for x in partial_col])
            if is_ok:
                upper_left.col -=1
            else:
                break

        while True:
            partial_col = self.get_row(row=upper_left.row-1, start_col=upper_left.col)
            is_ok = all([discriminator(x) for x in partial_col])
            if is_ok:
                upper_left.row -=1
            else:
                break

        return Region(upper_left=upper_left, lower_right=self.get_lower_right_index())

    def get_lower_right_index(self) -> Index:
        return Index(self.get_row_count()-1, self.get_row_len()-1)


    # -------------------------------------------
    # get rows/cols

    def get_row(self, row : int, start_col : int = 0):
        return self.content[row][start_col:]

    def get_col(self, col : int, start_row : int = 0):
        return [self.content[row][col] for row in range(start_row, self.get_row_count())]

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


if __name__ == "__main__":
    # Define three separate tables of sizes 2x2, 3x3, and 5x5 respectively, with blocks of '1's

    # 2x2 Table
    table_2x2 = [
        ["1", "1"],
        ["1", "0"]
    ]

    # 3x3 Table
    table_3x3 = [
        ["1", "0", "0"],
        ["1", "1", "1"],
        ["0", "1", "1"]
    ]

    table4x4 = [
        ["1", "1", "1", "0"],
        ["1", "1", "0", "0"],
        ["1", "0", "0", "0"],
        ["1", "1", "1", "1"]
    ]

    # 5x5 Table
    table_5x5 = [
        ["1", "1", "0", "0", "0"],
        ["1", "1", "1", "0", "0"],
        ["0", "1", "1", "1", "1"],
        ["0", "1", "1", "1", "1"],
        ["0", "1", "1", "1", "1"]
    ]

    test_disc = lambda x: x == '1'
    text_table = TextTable(table_5x5)
    # text_table.get_maximal_region(test_disc)

    print(text_table.get_lower_right_subtable(discriminator=test_disc))
    # text_table.get_maximal_region(discriminator=test_disc)