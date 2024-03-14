from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class Region:
    x_start : int
    y_start : int
    y_end : int
    x_end : int


@dataclass
class TextTable:
    content: list[list[str]]

    def __post_init__(self):
        if not all([len(row) == len(self.content[0]) for row in self.content]):
            raise ValueError("All rows must have the same length")

    def get_row_count(self) -> int:
        return len(self.content)

    def get_row_len(self) -> int:
        return len(self.content[0])

    def __getitem__(self, item):
        return self.content[item]


    def get_maximal_region(self, discriminator: Callable[[str], bool]) -> Region:
        pass


    def get_maximal_expansion(self, x_start: int, y_start, discriminator: Callable[[str], bool]) -> Region:
        x_end, y_end = x_start, y_start
        for col_num in range(x_start, self.get_row_len()):
            delta = self[y_start][col_num]
            print(f'col_num, delta : {col_num}, {delta}')
            if not discriminator(delta):
                break
            else:
                x_end = col_num

        for row_num in range(y_start, self.get_row_count()):
            delta = self[row_num][x_start:x_end]
            print(f'row_num, delta : {row_num}, {delta}')
            if not all([discriminator(x) for x in delta]):
                break
            else:
                y_end = row_num
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
