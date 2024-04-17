from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from .tables import TextTable, Region, Index, NumericalTable

# -------------------------------------------


@dataclass
class TableSelector:
    table : TextTable
    discriminator : Callable[[str], bool]


    @classmethod
    def get_numerical_subtable(cls, table : TextTable) -> NumericalTable:
        selector = TableSelector(table=table, discriminator=is_numeric)
        data_region = selector.get_lower_right_region()
        if not data_region:
            raise ValueError("No numerical data found")

        data =  table.get_subtable(region=data_region, dtype=float)
        preamble= ''
        for row_num in range(data_region.upper_left.row):
            row = table.get_row(row_num)
            preamble += ''.join(row)

        headers = ['' for _ in data_region.get_horizontal_indices()]
        for index, col_num in enumerate(data_region.get_horizontal_indices()):
            headers[index] = ''.join(table.get_col(col=col_num, end_row=data_region.upper_left.row-1))

        return NumericalTable(preable=preamble, headers=headers, data=data)


    def get_lower_right_region(self) -> Optional[Region]:
        region = self._get_lower_right_square()
        if region:
            region = self._get_upwards_expansion(region=region)
            # print(f'region is {region}')
            region=  self._get_leftwards_expansion(region=region)
        return region

    def _get_upwards_expansion(self, region : Region) -> Region:
        upper_left = region.upper_left
        lower_right = region.lower_right
        while upper_left.row-1 >= 0:
            partial_row = self.table.get_row(row=upper_left.row-1, start_col=upper_left.col, end_col=lower_right.col)
            is_ok = all([self.discriminator(x) for x in partial_row])
            if is_ok:
                upper_left.row -=1
            else:
                break
        return Region(upper_left=upper_left, lower_right=lower_right)


    def _get_leftwards_expansion(self, region : Region) -> Region:
        upper_left = region.upper_left
        lower_right = region.lower_right
        while upper_left.col-1 >= 0:
            partial_col = self.table.get_col(col=upper_left.col-1, start_row=upper_left.row, end_row=lower_right.row)
            is_ok = all([self.discriminator(x) for x in partial_col])
            if is_ok:
                upper_left.col -=1
            else:
                break
        return Region(upper_left=upper_left, lower_right=lower_right)


    def _get_lower_right_square(self) -> Optional[Region]:
        upper_left = None
        square_upper_left = self.table.get_lower_right_index()
        while True and square_upper_left.row>0 and square_upper_left.col>0:
            partial_row = self.table.get_row(square_upper_left.row, square_upper_left.col)
            failed_on_row = not all([self.discriminator(x) for x in partial_row])

            partial_col = self.table.get_col(square_upper_left.col, square_upper_left.row)
            failed_on_col = not all([self.discriminator(x) for x in partial_col])
            if not failed_on_row and not failed_on_col:
                upper_left = Index(row=square_upper_left.row,col=square_upper_left.col)
                square_upper_left.row -= 1
                square_upper_left.col -= 1
            else:
                break

        if not upper_left:
            region = None
        else:
            region = Region(upper_left=upper_left, lower_right=self.table.get_lower_right_index())
        return region



def is_numeric(text : str) -> bool:
    try:
        float(text)
        return True
    except:
        return False
