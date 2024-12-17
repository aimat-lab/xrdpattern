from __future__ import annotations

from dataclasses import dataclass


# -------------------------------------------


class CsvOrientations:
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'

@dataclass
class Matrix:
    headers : list[str]
    data : list[list[float]]

    def __post_init__(self):
        if not len(self.headers) == len(self.data[0]):
            raise ValueError(f"Number of headers ({len(self.headers)}) does not match number"
                             f" of data columns ({len(self.data)})")

    def get_x_values(self) -> list[float]:
        return self.data[0]

    def get_y_data(self, row : int) -> list[float]:
        if row == 0:
            raise ValueError('First row is reserved for x values')
        return self.data[row]

    def get_row_count(self) -> int:
        return len(self.data)

