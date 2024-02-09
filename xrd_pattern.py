from typing import Optional
from file_io import get_axrd_repr, Formats
import re

# -------------------------------------------


class XrdPattern:
    def __init__(self, filepath : Optional[str] = None):
        self.wave_length_angstrom : Optional[float] = None
        self.degree_over_intensity : list[(float,float)] = []
        self.xylib_repr : Optional[str] = None

        if filepath:
            self.import_from_file(filepath=filepath)


    def import_from_file(self,filepath : str):
        _ = self
        self.xylib_repr = get_axrd_repr(input_path=filepath, input_format=Formats.riet7)
        rows = [row for row in self.xylib_repr.split('\n') if not row.strip() == '']
        header_pattern = r'# column_1\tcolumn_2'

        try:
            header_match = re.findall(pattern=header_pattern, string=self.xylib_repr)[0]
        except Exception as e:
            raise ValueError(f"Could not find header matching pattern \"{header_pattern}\" in file {filepath}. Error: {str(e)}")

        header_row_index = rows.index(header_match)
        data_rows = rows[header_row_index+1:]
        for row in data_rows:

            deg_str, intensity_str = row.split()
            deg, intensity = float(deg_str), float(intensity_str)
            self.degree_over_intensity.append((deg, intensity))


    def export_as_json_file(self):
        pass


    def get_wavelength_angstrom(self) -> float:
        return self.wave_length_angstrom


    def get_standardized(self):
        pass

    def get_np_repr(self):
        if not self.degree_over_intensity:
            raise ValueError(f"Numpy array is None")

        return self.degree_over_intensity



if __name__ == "__main__":
    # xrd_pattern = XrdPattern(filepath="/home/daniel/aimat/pxrd_data/processed/example_files/asdf.raw")
    xrd_pattern = XrdPattern(filepath="/home/daniel/OneDrive/Downloads/Glass_wAS.dat")
    # print_supported_formats()