from __future__ import annotations

import csv
import math

from holytools.abstract import SelectableEnum

from xrdpattern.core import PatternData
from .table_selector import TableSelector, TextTable, NumericalTable


# -------------------------------------------

class Orientation(SelectableEnum):
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'

    @classmethod
    def from_manual_query(cls) -> Orientation:
        return super().from_manual_query()


class CsvParser:
    MAX_Q_VALUE = 60 # Two_theta = 180; lambda=0.21 Angstr
                     # Wavelength is k-alpha of W (Z=74); In practice no higher sources than Ag (Z=47) found

    def __init__(self, pattern_data_axis : Orientation):
        self.pattern_dimension : Orientation = pattern_data_axis

    def as_matrix(self, fpath : str) -> NumericalTable:
        data = []
        seperator = self.get_separator(fpath=fpath)

        with open(fpath, 'r', newline='') as infile:
            for line in infile:
                row = [item.strip() for item in line.strip().split(seperator)]
                if row and any(item for item in row):
                    data.append(row)

        if self.pattern_dimension == Orientation.VERTICAL:
            data = [list(col) for col in zip(*data)]
        table = TextTable(data)
        print(f'fpath,row, col length = {fpath} {table.get_row_count()}, {table.get_row_len()}')
        return TableSelector.get_numerical_subtable(table=table)


    def read_csv(self, fpath: str) -> list[PatternData]:
        matrix = self.as_matrix(fpath=fpath)
        x_axis_row = matrix.get_data(row=0)
        data_rows = [matrix.get_data(row=row) for row in range(1, matrix.get_row_count())]

        if len(data_rows) == 0:
            return []

        if not len(x_axis_row) == len(data_rows[0]):
            raise ValueError(f"X-axis row length {len(x_axis_row)} does not match data row length {len(data_rows[0])}")

        pattern_infos = []
        is_qvalues = max(x_axis_row) < CsvParser.MAX_Q_VALUE
        if is_qvalues:
            two_theta_degs = qvalues_to_angles(qvalues=x_axis_row)
        else:
            two_theta_degs = x_axis_row

        for intensities in data_rows:
            new = PatternData.from_intensitiy_map(two_theta_values=two_theta_degs, intensities=intensities)
            pattern_infos.append(new)

        x_axis_type = 'QValues' if is_qvalues else 'TwoThetaDegs'
        print(f'\nThe format of the csv file {fpath} was automatically recognized as:'
              f'\n- XAxisType: \"{x_axis_type}\"'
              f'\n- Csv Seperator : \"{CsvParser.get_separator(fpath=fpath)}\"')

        return pattern_infos


    @classmethod
    def has_two_columns(cls, fpath : str) -> bool:
        with open(fpath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) != 2:
                    return False
            return True

    @staticmethod
    def get_separator(fpath: str) -> str:
        with open(fpath, newline='') as csvfile:
            content = csvfile.read()
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(content)
            return str(dialect.delimiter)


#TODO replace this with copper wavelength from physical constants
copper_wavelength = 1.54

def qvalues_to_angles(qvalues : list[float]) -> list[float]:
    theta_values_rad = [math.asin(q*copper_wavelength)/(4*math.pi) for q in qvalues]
    two_theta_degs = [2*math.degrees(theta) for theta in theta_values_rad]

    return two_theta_degs
