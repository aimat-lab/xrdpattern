from typing import Optional
from file_io import get_axrd_repr, Formats
import re
import json
import numpy as np

# -------------------------------------------


class XrdPattern:
    def __init__(self, filepath : Optional[str] = None):
        self.wave_length_angstrom : Optional[float] = None
        self.degree_over_intensity : list = []

        if filepath:
            self.import_from_file(filepath=filepath)


    def import_from_file(self,filepath : str):
        _ = self
        xylib_repr = get_axrd_repr(input_path=filepath, input_format=Formats.bruker_raw)
        rows = [row for row in xylib_repr.split('\n') if not row.strip() == '']
        header_pattern = r'# column_1\tcolumn_2'

        try:
            header_match = re.findall(pattern=header_pattern, string=xylib_repr)[0]
        except Exception as e:
            raise ValueError(f"Could not find header matching pattern \"{header_pattern}\" in file {filepath}. Error: {str(e)}")

        header_row_index = rows.index(header_match)
        data_rows = rows[header_row_index+1:]
        for row in data_rows:

            deg_str, intensity_str = row.split()
            deg, intensity = float(deg_str), float(intensity_str)
            self.degree_over_intensity.append([deg, intensity])


    # def export_as_json_file(self):
    #     pass
    #
    #
    # def get_wavelength_angstrom(self) -> float:
    #     return self.wave_length_angstrom
    #
    #
    # def get_standardized(self):
    #     pass

    def get_np_repr(self):
        if not self.degree_over_intensity:
            raise ValueError(f"Numpy array is None")

        return np.array(self.degree_over_intensity)

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        obj = cls()
        obj.__dict__.update(data)
        return obj


if __name__ == "__main__":
    xrd_pattern = XrdPattern(filepath="/home/daniel/aimat/pxrd_data/processed/example_files/asdf.raw")
    # xrd_pattern = XrdPattern(filepath="/home/daniel/OneDrive/Downloads/Glass_wAS.dat")
    # print_supported_formats()
    print(xrd_pattern.__dict__)
    json_str = xrd_pattern.to_json()

    new_pattern = XrdPattern.from_json(json_str=json_str)
    print(new_pattern.__dict__)