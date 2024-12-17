from __future__ import annotations

from dataclasses import dataclass


# -------------------------------------------


class CsvOrientations:
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'

@dataclass
class Matrix:
    numerical_data : list[list[float]]

    def get_x_values(self) -> list[float]:
        return self.numerical_data[0]

    def get_y_data(self, row : int) -> list[float]:
        if row == 0:
            raise ValueError('First row is reserved for x values')
        return self.numerical_data[row]

    def get_row_count(self) -> int:
        return len(self.numerical_data)

