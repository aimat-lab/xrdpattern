from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from .tables import TextTable, Region, Index

# -------------------------------------------


@dataclass
class TableSelector:
    table : TextTable
    discriminator : Callable[[str], bool]

    def get_lower_right_region(self) -> Optional[Region]:
        region = self.get_lower_right_square()
        if region:
            region = self.get_upwards_expansion(region=region)
            region=  self.get_leftwards_expansion(region=region)
        return region

    def get_upwards_expansion(self, region : Region) -> Region:
        upper_left = region.upper_left
        lower_right = region.lower_right
        while True:
            partial_row = self.table.get_row(row=upper_left.row-1, start_col=upper_left.col, end_col=lower_right.col)
            is_ok = all([self.discriminator(x) for x in partial_row])
            if is_ok:
                upper_left.row -=1
            else:
                break
        return Region(upper_left=upper_left, lower_right=lower_right)


    def get_leftwards_expansion(self, region : Region) -> Region:
        upper_left = region.upper_left
        lower_right = region.lower_right
        while True:
            partial_col = self.table.get_col(col=upper_left.col-1, start_row=upper_left.row, end_row=lower_right.row)
            is_ok = all([self.discriminator(x) for x in partial_col])
            if is_ok:
                upper_left.col -=1
            else:
                break
        return Region(upper_left=upper_left, lower_right=lower_right)


    def get_lower_right_square(self) -> Optional[Region]:
        upper_left = None
        new_upper_left = self.table.get_lower_right_index()
        while True:
            partial_row = self.table.get_row(new_upper_left.row, new_upper_left.col)
            failed_on_row = not all([self.discriminator(x) for x in partial_row])

            partial_col = self.table.get_col(new_upper_left.col, new_upper_left.row)
            failed_on_col = not all([self.discriminator(x) for x in partial_col])
            if not failed_on_row and not failed_on_col:
                upper_left = Index(row=new_upper_left.row,col=new_upper_left.col)
                new_upper_left.row -= 1
                new_upper_left.col -= 1
            else:
                break

        if not upper_left:
            region = None
        else:
            region = Region(upper_left=upper_left, lower_right=self.table.get_lower_right_index())
        return region
