from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline


class IntensityMap(dict[float,float]):

    def get_standardized(self, start_val : float, stop_val : float, num_entries : int) -> IntensityMap:
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
        return IntensityMap(mapping)
