from __future__ import annotations

import math
import numpy as np
from copy import copy
from dataclasses import dataclass
from scipy.interpolate import CubicSpline
from hollarek.abstract import SelectableEnum, JsonDataclass
# -------------------------------------------

class XAxisType(SelectableEnum):
    TwoTheta = 'TwoTheta'
    QValues = 'QValues'


@dataclass
class IntensityMap(JsonDataclass):
    data : dict[float, float]
    x_axis_type : XAxisType

    def get_standardized(self, start_val : float, stop_val : float, num_entries : int) -> IntensityMap:
        x_values = list(self.data.keys())
        start, end = x_values[0], x_values[-1]
        std_angles = np.linspace(start=start_val, stop=stop_val, num=num_entries)

        x = np.array(list(self.data.keys()))
        y = np.array(list(self.data.values()))
        cs = CubicSpline(x, y)

        interpolated_intensities = [cs(angle) for angle in std_angles if start <= angle <= end]
        max_intensity = max(interpolated_intensities) if interpolated_intensities else 1

        mapping = {}
        for angle in std_angles:
            if angle < start or angle > end:
                mapping[angle] = 0
            else:
                mapping[angle] = cs(angle) / max_intensity
        return IntensityMap(data=mapping, x_axis_type=self.x_axis_type)


    def convert_axis(self, target_axis_type: XAxisType, wavelength: float) -> IntensityMap:
        if self.x_axis_type == target_axis_type:
            return copy(self)

        if target_axis_type == XAxisType.QValues:
            convert = lambda val : self.twotheta_to_q(val, wavelength)
        else:
            convert = lambda val : self.q_to_twotheta(val, wavelength)

        new_data = {}
        for old_val, intensity in self.data.items():
            new_val = convert(old_val)
            new_data[new_val] = intensity

        return IntensityMap(data=new_data, x_axis_type=target_axis_type)

    # -------------------------------------------

    @staticmethod
    def q_to_twotheta(q: float, wavelength: float) -> float:
        theta = math.asin(q * wavelength / (4 * math.pi))
        two_theta = 2 * math.degrees(theta)
        return two_theta

    @staticmethod
    def twotheta_to_q(two_theta: float, wavelength: float) -> float:
        theta_rad = math.radians(two_theta / 2)
        q = (4 * math.pi * math.sin(theta_rad)) / wavelength
        return q


    def as_list_pair(self) -> (list[float], list[float]):
        x_values = list(self.data.keys())
        y_values = list(self.data.values())
        return x_values, y_values