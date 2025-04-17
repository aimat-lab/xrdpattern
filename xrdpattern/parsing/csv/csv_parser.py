from __future__ import annotations

import csv
import math

import pandas as pd

from xrdpattern.parsing.csv.matrix import Matrix, CsvOrientations
from xrdpattern.xrd import XrdData, XrdAnode, XrayInfo

copper_xray_info  = XrayInfo.from_anode(element=XrdAnode.Cu)
copper_wavelength = copper_xray_info.primary_wavelength

# -------------------------------------------


class CsvParser:
    MAX_Q_VALUE = 60 # Two_theta = 180; lambda=0.21 Angstr;  Wavelength is k-alpha of W (Z=74); In practice no higher sources than Ag (Z=47) found

    def extract_multi(self, fpath: str, pattern_dimension : str) -> list[XrdData]:
        matrix = self._as_matrix(fpath=fpath, pattern_orientation=pattern_dimension)
        x_axis_row = matrix.get_x_values()
        y_axis_rows = [matrix.get_y_data(row=row) for row in range(1, matrix.get_row_count())]

        if len(y_axis_rows) == 0:
            return []
        if not len(x_axis_row) == len(y_axis_rows[0]):
            raise ValueError(f"X-axis row length {len(x_axis_row)} does not match data row length {len(y_axis_rows[0])}")

        is_qvalues = max(x_axis_row) < CsvParser.MAX_Q_VALUE
        x_axis_type = 'QValues' if is_qvalues else 'TwoThetaDegs'
        print(f'The format of the csv file {fpath} was automatically determined/specified as:'
              f'\n- XAxisType     : \"{x_axis_type}\"'
              f'\n- Csv Seperator : \"{CsvParser.get_separator(fpath=fpath)}\"'
              f'\n- Orientation   : \"{pattern_dimension}\"')

        if is_qvalues:
            two_theta_degs = qvalues_to_copper_angles(qvalues=x_axis_row)
        else:
            two_theta_degs = x_axis_row

        pattern_infos = []
        for intensities in y_axis_rows:
            new = XrdData.make_unlabeled(two_theta_values=two_theta_degs, intensities=intensities)
            if is_qvalues:
                new.powder_experiment.xray_info = copper_xray_info
            pattern_infos.append(new)

        return pattern_infos

    def _as_matrix(self, fpath: str, pattern_orientation : str) -> Matrix:
        table = []
        seperator = self.get_separator(fpath=fpath)

        with open(fpath, 'r', newline='') as f:
            for line in f:
                row = [item.strip() for item in line.strip().split(seperator)]
                if row and any(item for item in row):
                    table.append(row)

        if self.is_numerical(values=table[0]):
            numerical_part = table
        else:
            numerical_part = table[1:]

        if pattern_orientation == CsvOrientations.VERTICAL:
            numerical_part = [list(col) for col in zip(*numerical_part)]
        data = self.to_numerical(numerical_part)
        matrix = Matrix( numerical_data=data)

        delta = len(numerical_part) - len(matrix.numerical_data)
        if delta > 0:
            print(f'Warning: In {fpath}, {delta} rows were skipped due to non-numerical values')

        return matrix

    # -------------------------------------------
    # csv tools

    @staticmethod
    def get_separator(fpath: str) -> str:
        with open(fpath, newline='') as csvfile:
            content = csvfile.read()
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(content)
            return str(dialect.delimiter)

    @classmethod
    def has_two_columns(cls, fpath : str) -> bool:
        with open(fpath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) != 2:
                    return False
            return True

    @staticmethod
    def xlsx_to_csv(xlsx_fpath : str, csv_fpath : str):
        data = pd.read_excel(xlsx_fpath)
        data.to_csv(csv_fpath, index=False, sep=';')

    # ------------------------------------------
    # datatype tools

    @staticmethod
    def is_numerical(values : list[str]) -> bool:
        try:
            for x in values:
                float(x)
            return True
        except:
            return False

    def to_numerical(self, data : list[list[str]], row_start : int = 0) -> list[list[float]]:
        numerical_data = []
        for row_num, row in enumerate(data):
            try:
                float_data = [self.convert_to_float(x, row_num + row_start + 1, col_num + 1) for col_num, x in enumerate(row)]
            except Exception:
                continue
            numerical_data.append(float_data)



        return numerical_data

    @staticmethod
    def convert_to_float(x : str, row_num : int, col_num : int) -> float:
        try:
            return float(x)
        except Exception:
            raise ValueError(f"Could not convert value \"{x}\" at row {row_num}, column {col_num} to a numerical value")


def qvalues_to_copper_angles(qvalues : list[float]) -> list[float]:
    theta_values_rad = [math.asin(q*copper_wavelength/(4*math.pi)) for q in qvalues]
    two_theta_degs = [2*math.degrees(theta) for theta in theta_values_rad]

    return two_theta_degs
