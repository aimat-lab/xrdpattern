from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from holytools.abstract import JsonDataclass
from scipy.interpolate import CubicSpline


# -------------------------------------------


@dataclass
class XrdIntensities(JsonDataclass):
    twotheta_mapping : dict[float, float]

    @classmethod
    def from_angle_data(cls, twotheta_map : dict[float, float]):
        return cls(twotheta_mapping=twotheta_map)

    def get_standardized(self, start_val : float, stop_val : float, num_entries : int) -> XrdIntensities:
        x_values = list(self.twotheta_mapping.keys())
        start, end = x_values[0], x_values[-1]
        std_angles = np.linspace(start=start_val, stop=stop_val, num=num_entries)

        x = np.array(list(self.twotheta_mapping.keys()))
        y = np.array(list(self.twotheta_mapping.values()))
        min_val = min(y)
        y = y - min_val

        cs = CubicSpline(x, y)

        interpolated_intensities = [cs(angle) for angle in std_angles if start <= angle <= end]
        max_intensity = max(interpolated_intensities)
        normalization_factor = max_intensity if max_intensity != 0 else 1

        mapping = {}
        for angle in std_angles:
            if angle < start or angle > end:
                mapping[angle] = float(0)
            else:
                mapping[angle] = cs(angle) / normalization_factor
        return XrdIntensities(twotheta_mapping=mapping)


    def as_list_pair(self) -> (list[float], list[float]):
        x_values = list(self.twotheta_mapping.keys())
        y_values = list(self.twotheta_mapping.values())
        return x_values, y_values


    def __eq__(self, other):
        if not isinstance(other, XrdIntensities):
            return False

        return self.twotheta_mapping == other.twotheta_mapping

if __name__ == '__main__':
    pass