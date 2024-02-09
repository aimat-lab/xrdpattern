import logging
from typing import Optional
from file_io import get_xy_repr, Formats
import re
import json
import numpy as np
from datetime import datetime
from dataclasses import dataclass

# -------------------------------------------

@dataclass
class Metadata:
    primary_wavelength : float
    secondary_wavelength : float
    primary_to_secondary_ratio : float
    anode_material : str
    measurement_datetime : datetime

    def read_from_header_str(self, header_str: str):
        for line in header_str.splitlines():
            if line.startswith('#'):
                key_value = line[1:].split(':', 1)  # Split at the first ':' only
                if len(key_value) == 2:
                    key, value = key_value
                    key = key.strip()
                    value = value.strip()
                    if key == 'ALPHA1':
                        self.primary_wavelength = float(value)
                    elif key == 'ALPHA2':
                        self.secondary_wavelength = float(value)
                    elif key == 'ALPHA_RATIO':
                        self.primary_to_secondary_ratio = float(value)
                    elif key == 'ANODE_MATERIAL':
                        self.anode_material = value
                    elif key == 'MEASURE_DATE' or key == 'MEASURE_TIME':
                        if not hasattr(self, 'measurement_datetime'):
                            # Combine date and time if both are present
                            date_str = header_str.split('# MEASURE_DATE: ')[1].split('\n')[0].strip()
                            time_str = header_str.split('# MEASURE_TIME: ')[1].split('\n')[0].strip()
                            combined_str = date_str + ' ' + time_str
                            self.measurement_datetime = datetime.strptime(combined_str, '%m/%d/%Y %H:%M:%S')


class XrdPattern:
    standard_entries_num = 1000
    std_angle_start = 0
    std_angle_end = 180

    def __init__(self, filepath : Optional[str] = None):
        self.wave_length_angstrom : Optional[float] = None
        self.degree_over_intensity : list = []
        self.measurement_timestamp : Optional[datetime] = None

        if filepath:
            self.import_from_file(filepath=filepath)


    def import_from_file(self, filepath : str):
        suffix = filepath.split('.')[-1]
        if suffix == Formats.aimat_json.suffix:
            self.import_from_json(filepath=filepath)
        else:
            self.import_from_data_file(filepath=filepath)


    def import_from_json(self, filepath : str):
        with open(filepath, 'r') as file:
            data = file.read()
            self.__dict__.update(json.loads(data))


    def import_from_data_file(self, filepath : str):
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

        # print(xylib_repr)


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
    # get

    def get_wavelength_angstrom(self) -> float:
        if self.wave_length_angstrom is None:
            raise ValueError(f"Wavelength is None")

        return self.wave_length_angstrom


    def get_np_repr(self):
        if not self.degree_over_intensity:
            raise ValueError(f"Numpy array is None")

        return np.array(self.degree_over_intensity)


    def to_json(self) -> str:
        data = self.__dict__
        return json.dumps(data)


    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        obj = cls()
        obj.__dict__.update(data)
        print(obj.__dict__)

        return obj


    def get_standardized(self) -> list:
        pass


if __name__ == "__main__":
    xrd_pattern = XrdPattern(filepath="/home/daniel/aimat/pxrd_data/processed/example_files/asdf.raw")
    # xrd_pattern.export_as_json(filepath='test3')
    # xrd_pattern = XrdPattern(filepath="/home/daniel/OneDrive/Downloads/Glass_wAS.dat")
    # print(xrd_pattern.__dict__)
    # test_json = xrd_pattern.to_json()
    #
    # new_pattern = XrdPattern.from_json(json_str=test_json)
    # print(new_pattern.__dict__)
    # xrd_pattern.export_as_json(filepath='test')
    # new_pattern = XrdPattern(filepath='test3.json')
    # print(new_pattern.to_json())
    #
    # new_pattern.export_as_json(filepath='test2')