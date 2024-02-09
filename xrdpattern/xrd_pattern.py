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

        if filepath:
            self.import_from_file(filepath=filepath)


    def import_from_file(self, filepath : str):
        suffix = filepath.split('.')[-1]
        if suffix == Formats.aimat_json.suffix:
            self._initialize_from_json(filepath=filepath)
        else:
            self._import_from_data_file(filepath=filepath)
        log_xrd_info(msg=self.get_import_report())

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

    def get_import_report(self):
        report_str = '[Errors]:'
        if self.metadata.primary_wavelength_angstrom is None:
            report_str += "Primary wavelength missing! \n"

        if len(self.degree_over_intensity) == 0:
            report_str += "No data found. Degree over intensity is empty! \n"

        elif len(self.degree_over_intensity) < 10:
            report_str += "Data is too short. Less than 10 entries! \n"


        report_str = '[Warnings]:\n'
        if self.metadata.secondary_wavelength_angstrom is None:
            report_str += "No secondary wavelength found\n"
        if self.metadata.anode_material is None:
            report_str += "No anode material found\n"
        if self.metadata.measurement_datetime is None:
            report_str += "No measurement datetime found\n"
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