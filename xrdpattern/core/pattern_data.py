from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline
from holytools.abstract import JsonDataclass
from dataclasses import dataclass, fields
from typing import Optional

from xrdpattern.powder import PatternLabel

# -------------------------------------------

@dataclass
class PatternData(JsonDataclass):
    two_theta_values : list[float]
    intensities : list[float]
    label : PatternLabel
    name : Optional[str] = None

    @classmethod
    def from_intensitiy_map(cls, two_theta_values: list[float], intensities: list[float]) -> PatternData:
        metadata = PatternLabel.make_empty()
        return cls(two_theta_values=two_theta_values, intensities=intensities, label=metadata)

    def to_dict(self):
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def get_standardized_map(self, start_val : float, stop_val : float, num_entries : int) -> (list[float], list[float]):
        start, end = self.two_theta_values[0], self.two_theta_values[-1]
        std_angles = np.linspace(start=start_val, stop=stop_val, num=num_entries)

        x = np.array(self.two_theta_values)
        y = np.array(self.intensities)
        min_val = min(y)
        y = y - min_val

        cs = CubicSpline(x, y)
        interpolated_intensities = [cs(angle) for angle in std_angles if start <= angle <= end]
        max_intensity = max(interpolated_intensities)
        normalization_factor = max_intensity if max_intensity != 0 else 1

        std_intensities = []
        for angle in std_angles:
            I = cs(angle)/normalization_factor if start <= angle <= end else float(0)
            std_intensities.append(I)

        return std_angles,std_intensities


    def __eq__(self, other : PatternData):
        if not isinstance(other, PatternData):
            return False

        angles_equal = self.two_theta_values == other.two_theta_values
        intensities_equal = self.intensities == other.intensities

        return angles_equal and intensities_equal


if __name__ == '__main__':
    pass