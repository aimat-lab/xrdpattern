from typing import Optional
from file_io import get_repr, Formats
import re

# -------------------------------------------


class XrdPattern:
    def __init__(self, filepath : Optional[str] = None):
        self.wave_length_angstrom : Optional[float] = None
        self.degree_over_intensity : list[(float,float)] = []
        self.source_file : Optional[bytes] = None

        if filepath:
            self.import_from_file(filepath=filepath)


    def import_from_file(self,filepath : str):
        _ = self
        xy_content = get_repr(input_path=filepath, xrd_format=Formats.XSYG)
        rows = [row for row in xy_content.split('\n') if not row.strip() == '']
        header_pattern = r'# column_1\tcolumn_2'

        try:
            header_match = re.findall(pattern=header_pattern, string=xy_content)[0]
        except Exception as e:
            raise ValueError(f"Could not find header matching pattern \"{header_pattern}\" in file {filepath}. Error: {str(e)}")

        header_row_index = rows.index(header_match)
        data_rows = rows[header_row_index+1:]
        for row in data_rows:

            deg_str, intensity_str = row.split()
            deg, intensity = float(deg_str), float(intensity_str)
            self.degree_over_intensity.append((deg, intensity))

        print(self.degree_over_intensity)


    def export_to_file(self):
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
    xrd_pattern = XrdPattern(filepath="/home/daniel/aimat/pxrd_data/processed/example_files/asdf.raw")
