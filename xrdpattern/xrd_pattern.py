from typing import Optional
from xrd_file_io import get_xy_repr, Formats, Metadata
import re
import json
import numpy as np
from xrd_file_io import write_to_json
from xrd_file_io.xrd_types import Mapping
from xrd_logger import log_xrd_info
from xrd_logger.report import Report, get_report
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
# -------------------------------------------


class XrdPattern:
    standard_entries_num = 1000
    std_angle_start = 0
    std_angle_end = 90

    def __init__(self, filepath : Optional[str] = None):
        self.twotheta_to_intensity : Mapping = {}
        self.metadata : Optional[Metadata] = None
        self.processing_report : Optional[Report] = None

        if filepath:
            self.import_from_file(filepath=filepath)


    def import_from_file(self, filepath : str):
        suffix = filepath.split('.')[-1]
        if suffix == Formats.aimat_json.suffix:
            self._initialize_from_json(filepath=filepath)
        else:
            self._import_from_data_file(filepath=filepath)
        log_msg = str(get_report(filepath=filepath, metadata=self.metadata, deg_over_intensity=self.twotheta_to_intensity))
        log_xrd_info(msg=log_msg)


    def export_as_json(self, filepath : str):
        write_to_json(filepath=filepath, content=self.to_json())


    def plot(self, use_interpolation=True):
        if use_interpolation:
            std_mapping = self.get_standardized_mapping()
            angles = list(std_mapping.keys())
            intensities = list(std_mapping.values())
            label = 'Interpolated Intensity'
        else:
            angles = list(self.twotheta_to_intensity.keys())
            intensities = list(self.twotheta_to_intensity.values())
            label = 'Original Intensity'

        plt.figure(figsize=(10, 6))
        plt.plot(angles, intensities, label=label)
        plt.xlabel('Angle (Degrees)')
        plt.ylabel('Intensity')
        plt.title('XRD Pattern')
        plt.legend()
        plt.show()

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
            self.twotheta_to_intensity[deg] = intensity

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

    def get_primary_wavelength_angstrom(self) -> float:
        if self.metadata.primary_wavelength_angstrom is None:
            raise ValueError(f"Wavelength is None")

        return self.metadata.primary_wavelength_angstrom


    def to_json(self) -> str:
        data = self.__dict__
        return json.dumps(data)


    def get_standardized_mapping(self) -> Mapping:
        """
        :return: Mapping from 2 theta to intensity with theta in [0,90] and intensity in [0,1] by padding missing angle range with 0, interpolating the intensity and then normalizing it by diving through the max intensity
        """
        angles = list(self.twotheta_to_intensity.keys())
        start_angle, end_angle =  angles[0], angles[-1]

        std_angles = np.linspace(start=XrdPattern.std_angle_start,
                                          stop=XrdPattern.std_angle_end,
                                          num= 1000)

        x = np.array(list(self.twotheta_to_intensity.keys()))
        y = np.array(list(self.twotheta_to_intensity.values()))
        cs = CubicSpline(x, y)

        interpolated_intensities = [cs(angle) for angle in std_angles if start_angle <= angle <= end_angle]
        max_intensity = max(interpolated_intensities) if interpolated_intensities else 1

        std_intensity_mapping = {}
        for angle in std_angles:
            if angle < start_angle or angle > end_angle:
                std_intensity_mapping[angle] = 0
            else:
                std_intensity_mapping[angle] = cs(angle) / max_intensity

        return std_intensity_mapping


if __name__ == "__main__":
    xrd_pattern = XrdPattern(filepath="/home/daniel/aimat/pxrd_data/processed/example_files/asdf.raw")
    print(xrd_pattern.get_standardized_mapping())
    xrd_pattern.plot()