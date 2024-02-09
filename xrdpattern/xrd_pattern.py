import logging
from typing import Optional
from file_io import get_xy_repr, Formats
import re
import json
import numpy as np
# from datetime import datetime
from file_io.metadata import Metadata
from xrd_logger import log_xrd_info

# -------------------------------------------

class XrdPattern:
    standard_entries_num = 1000
    std_angle_start = 0
    std_angle_end = 180



    def __init__(self, filepath : Optional[str] = None):
        self.degree_over_intensity : list = []
        self.metadata : Optional[Metadata] = None
        self.has_errors : Optional[bool] = None
        self.has_warnings : Optional[bool] = None

        if filepath:
            self.import_from_file(filepath=filepath)


    def import_from_file(self, filepath : str):
        suffix = filepath.split('.')[-1]
        if suffix == Formats.aimat_json.suffix:
            self._initialize_from_json(filepath=filepath)
        else:
            self._import_from_data_file(filepath=filepath)
        log_msg = self.make_report_and_set_flags(filepath=filepath)
        log_xrd_info(msg=log_msg)

    def export_as_json(self, filepath : str):
        try:
            base_path = filepath.split('.')[0]
            filepath_suffix= filepath.split('.')[-1]

            if filepath_suffix != Formats.aimat_json.suffix:
                raise ValueError(f"Invalid file ending for json export")

        except:
            logging.warning(f"Invalid json export path {filepath}. Correcting to json suffix path")
            base_path = filepath
            filepath_suffix = Formats.aimat_json.suffix

        write_path = f'{base_path}.{filepath_suffix}'
        try:
            with open(write_path, 'w') as file:
                file.write(self.to_json())
        except:
            raise ValueError(f"Could not write to file {filepath}")

    # -------------------------------------------
    # import methods

    def _initialize_from_json(self, filepath : str):
        with open(filepath, 'r') as file:
            data = file.read()
            self.__dict__.update(json.loads(data))


    def _import_from_data_file(self, filepath : str):
        _ = self
        xylib_repr = get_xy_repr(input_path=filepath, input_format_hint=Formats.bruker_raw)
        column_pattern = r'# column_1\tcolumn_2'

        try:
            column_match = re.findall(pattern=column_pattern, string=xylib_repr)[0]
        except Exception as e:
            raise ValueError(f"Could not find header matching pattern \"{column_pattern}\" in file {filepath}. Error: {str(e)}")

        header_str, data_str = xylib_repr.split(column_match)
        data_rows = [row for row in data_str.split('\n') if not row.strip() == '']
        for row in data_rows:
            deg_str, intensity_str = row.split()
            deg, intensity = float(deg_str), float(intensity_str)
            self.degree_over_intensity.append([deg, intensity])

        self.metadata = Metadata(header_str=header_str)


    @classmethod
    def from_json_str(cls, json_str: str):
        data = json.loads(json_str)
        obj = cls()
        obj.__dict__.update(data)
        print(obj.__dict__)

        return obj

    # -------------------------------------------
    # get

    def make_report_and_set_flags(self, filepath : str):
        report_str = f'Successfully processed file {filepath}'
        self.has_errors = True
        self.has_warnings = True

        error_start = '- Errors:'
        error_str = error_start
        if self.metadata.primary_wavelength_angstrom is None:
            error_str += "\nPrimary wavelength missing!"

        if len(self.degree_over_intensity) == 0:
            error_str += "\nNo data found. Degree over intensity is empty!"

        elif len(self.degree_over_intensity) < 10:
            error_str += "\nData is too short. Less than 10 entries!"

        if error_str == error_start:
            error_str = f'\nNo errors found: Wavelength and data successfully parsed'
            self.has_errors = False
        report_str += error_str

        warning_start = '- Warnings:'
        warning_str = warning_start
        if self.metadata.secondary_wavelength_angstrom is None:
            warning_str += "\nNo secondary wavelength found"
        if self.metadata.anode_material is None:
            warning_str += "\nNo anode material found"
        if self.metadata.measurement_datetime is None:
            warning_str += "\nNo measurement datetime found"

        if warning_str == warning_start:
            warning_str = f'\nNo warnings found: All metadata was successfully parsed'
            self.has_warnings = False

        report_str += warning_str

        return report_str


    def get_primary_wavelength_angstrom(self) -> float:
        if self.metadata.primary_wavelength_angstrom is None:
            raise ValueError(f"Wavelength is None")

        return self.metadata.primary_wavelength_angstrom


    def get_np_repr(self):
        if not self.degree_over_intensity:
            raise ValueError(f"Numpy array is None")

        return np.array(self.degree_over_intensity)


    def to_json(self) -> str:
        data = self.__dict__
        return json.dumps(data)


    def get_standardized(self) -> list:
        pass


if __name__ == "__main__":
    xrd_pattern = XrdPattern(filepath="/home/daniel/aimat/pxrd_data/processed/example_files/asdf.raw")