from __future__ import annotations
from dataclasses import dataclass
from hollarek.abstract import SelectableEnum

from xrdpattern.core import XAxisType, XrdIntensities, Metadata, PatternInfo
from .table_selector import TableSelector, TextTable, NumericalTable
import csv
# -------------------------------------------

class Orientation(SelectableEnum):
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'


    @classmethod
    def from_manual_query(cls) -> Orientation:
        return super().from_manual_query()


class Seperator(SelectableEnum):
    COMMA = ','
    SEMICOLON = ';'
    TAB = '\t'

    @classmethod
    def from_manual_query(cls) -> Seperator:
        return super().from_manual_query()

@dataclass
class CsvScheme:
    pattern_dimension : Orientation
    x_axis_type: XAxisType = XAxisType.TwoTheta
    seperator: Seperator = Seperator.COMMA

    @classmethod
    def from_manual(cls) -> CsvScheme:
        print(f'Please specify csv scheme')
        x_axis_type = XAxisType.from_manual_query()
        pattern_dimension = Orientation.from_manual_query()
        seperator = Seperator.from_manual_query()
        return CsvScheme(x_axis_type=x_axis_type, pattern_dimension=pattern_dimension, seperator=seperator)


class CsvParser:
    def __init__(self, csv_scheme : CsvScheme):
        self.csv_scheme : CsvScheme = csv_scheme

    def as_matrix(self, fpath : str) -> NumericalTable:
        data = []
        with open(fpath, 'r', newline='') as infile:
            for line in infile:
                row = [item.strip() for item in line.strip().split(self.csv_scheme.seperator.value)]
                if row and any(item for item in row):
                    data.append(row)

        if self.csv_scheme.pattern_dimension == Orientation.HORIZONTAL:
            data = [list(col) for col in zip(*data)]
        table = TextTable(data)
        print(f'fpath,row, col length = {fpath} {table.get_row_count()}, {table.get_row_len()}')
        return TableSelector.get_numerical_subtable(table=table)


    def read_csv(self, fpath: str) -> list[PatternInfo]:
        matrix = self.as_matrix(fpath=fpath)
        x_axis_row = matrix.get_data(row=0)
        data_rows = [matrix.get_data(row=row) for row in range(1, matrix.get_row_count())]

        if len(data_rows) == 0:
            return []

        if not len(x_axis_row) == len(data_rows[0]):
            raise ValueError(f"X-axis row length {len(x_axis_row)} does not match data row length {len(data_rows[0])}")

        patterns = []
        for row in data_rows:
            data = {x : y for (x,y) in zip(x_axis_row, row)}
            intensity_map = XrdIntensities(data=data, x_axis_type=self.csv_scheme.x_axis_type)
            new = PatternInfo(xrd_intensities=intensity_map, metadata=Metadata.make_empty())
            patterns.append(new)
        return patterns

    @classmethod
    def has_two_columns(cls, fpath : str) -> bool:
        with open(fpath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) != 2:
                    return False
            return True