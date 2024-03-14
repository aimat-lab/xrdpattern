from __future__ import annotations

import numpy as np
from typing import Optional
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
from dataclasses import dataclass

from hollarek.templates import JsonDataclass
from xrdpattern.xrd_data.metadata import Metadata

from enum import Enum
# -------------------------------------------

class XAxisType(Enum):
    TwoTheta = 'TwoTheta'
    QValues = 'QValues'

@dataclass
class XrdPattern(JsonDataclass):
    twotheta_to_intensity : dict[float, float]
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

    def get_wavelength(self, primary : bool = True) -> float:
        wavelength_info = self.metadata.wavelength_info
        if primary:
            wavelength = wavelength_info.primary
        else:
            wavelength = wavelength_info.secondary
        if wavelength is None:
            raise ValueError(f"Wavelength is None")

        return wavelength


    def get_data(self, apply_standardization = True, x_axis_type :  XAxisType = XAxisType.TwoTheta) -> RealValuedMap:
        """
        :param apply_standardization: Standardization pads missing values, scales intensity into [0,1] range and makes x-step size uniform
        :param x_axis_type: Specifies the type of x-axis values, defaults to XAxisType.TwoTheta. This determines how the x-axis is interpreted and processed.
        :return: A mapping from the specified x-axis type to intensity
        """
        if x_axis_type == XAxisType.QValues:
            raise NotImplementedError

        mapping = RealValuedMap(self.twotheta_to_intensity)
        if apply_standardization:
            start, stop, num_entries = 0, 90, 1000
            mapping = mapping.get_standardized(start_val=start, stop_val=stop, num_entries=num_entries)

        return RealValuedMap(mapping)

    # -------------------------------------------

    def save(self, fpath : str):
        with open(fpath, 'w') as f:
            f.write(self.to_str())


class RealValuedMap(dict[float,float]):

    def get_standardized(self, start_val : float, stop_val : float, num_entries : int) -> RealValuedMap:
        angles = list(self.keys())
        start_angle, end_angle = angles[0], angles[-1]

        std_angles = np.linspace(start=start_val, stop=stop_val, num=num_entries)

        x = np.array(list(self.keys()))
        y = np.array(list(self.values()))
        cs = CubicSpline(x, y)

        interpolated_intensities = [cs(angle) for angle in std_angles if start_angle <= angle <= end_angle]
        max_intensity = max(interpolated_intensities) if interpolated_intensities else 1

        mapping = {}
        for angle in std_angles:
            if angle < start_angle or angle > end_angle:
                mapping[angle] = 0
            else:
                mapping[angle] = cs(angle) / max_intensity
        return RealValuedMap(mapping)
