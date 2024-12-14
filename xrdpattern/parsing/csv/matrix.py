from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# -------------------------------------------


class Orientation(Enum):
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

    def get_data(self, row : int) -> list[float]:
        return self.data[row]

    def get_row_count(self) -> int:
        return len(self.data)

