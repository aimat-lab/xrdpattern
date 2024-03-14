from __future__ import annotations

import numpy as np
from typing import Optional
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
from dataclasses import dataclass

from hollarek.templates import JsonDataclass
from xrdpattern.xrd_data.metadata import Metadata

# -------------------------------------------

@dataclass
class XrdPattern(JsonDataclass):
    twotheta_to_intensity : dict
    metadata: Metadata
    datafile_path : Optional[str] = None


    def plot(self, use_interpolation=True):
        if use_interpolation:
            std_mapping = self.get_data()
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
    # get

    def get_primary_wavelength_angstrom(self) -> float:
        if self.metadata. is None:
            raise ValueError(f"Wavelength is None")

        return self.metadata.primary_wavelength


    def get_data(self) -> RealValuedMap:
        """
        :return: Mapping from 2 theta to intensity with theta in [0,90] and intensity in [0,1] by padding missing angle range with 0, interpolating the intensity and then normalizing it by diving through the max intensity
        """
        standard_entries_num = 1000
        std_angle_start = 0
        std_angle_end = 90

        angles = list(self.twotheta_to_intensity.keys())
        start_angle, end_angle =  angles[0], angles[-1]

        std_angles = np.linspace(start=std_angle_start,
                                 stop=std_angle_end,
                                 num= standard_entries_num)

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

        return RealValuedMap(std_intensity_mapping)

    # -------------------------------------------

    def save(self, fpath : str):
        with open(fpath, 'w') as f:
            f.write(self.to_str())


class RealValuedMap(dict[float,float]):
    pass

