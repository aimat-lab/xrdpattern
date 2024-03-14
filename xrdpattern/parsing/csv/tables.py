from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class Region:
    x_start : int
    y_start : int
    y_end : int
    x_end : int

    @classmethod
    def create_empty(cls):
        return Region(0,0,0,0)

    def is_empty(self) -> bool:
        return self.x_start == self.x_end and self.y_start == self.y_end

    def get_indices(self) -> set[(int,int)]:
        x_list = range(self.x_start, self.x_end)
        y_list = range(self.y_start, self.y_end)
        return {(x,y) for x in x_list for y in y_list}

    def get_size(self) -> int:
        return (self.x_end-self.x_start)*(self.y_end-self.y_start)

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
        starting_points = [(row,col) for row in range(self.get_row_count()) for col in range(self.get_row_len())]

        maximal_region = Region.create_empty()
        discarded_points = set()
        for x,y in starting_points:
            if (x,y) in discarded_points:
                continue
            row, col = starting_points.pop()
            region = self.get_maximal_expansion(start_col=col, start_row=row, discriminator=discriminator)
            discarded_points.update(region.get_indices())
            if maximal_region.get_size() < region.get_size():
                maximal_region = region
                print(region.get_size())
                print(f'x,y = {x,y}')
                print(maximal_region)

        # print(maximal_region)
        return maximal_region

    def get_maximal_expansion(self, start_col: int, start_row, discriminator: Callable[[str], bool]) -> Region:
        x_end, y_end = start_col, start_row
        for col_num in range(start_col, self.get_row_len()):
            delta = self[start_row][col_num]
            # print(f'col_num, delta : {col_num}, {delta}')
            if not discriminator(delta):
                break
            else:
                x_end = col_num

        for row_num in range(start_row, self.get_row_count()):
            delta = self[row_num][start_col:x_end]
            # print(f'row_num, delta : {row_num}, {delta}')
            if not all([discriminator(x) for x in delta]):
                break
            else:
                y_end = row_num
        return Region(x_start=start_col, y_start=start_row, x_end=x_end, y_end=y_end)


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
        ["1", "1", "0"],
        ["1", "1", "1"],
        ["0", "1", "0"]
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
        ["0", "0", "1", "1", "1"],
        ["0", "0", "1", "1", "1"]
    ]

    test_disc = lambda x: x == '1'
    text_table = TextTable(table_5x5)
    # text_table.get_maximal_region(test_disc)

    print(text_table.get_maximal_expansion(start_col=0, start_row=0, discriminator=test_disc))
    # text_table.get_maximal_region(discriminator=test_disc)