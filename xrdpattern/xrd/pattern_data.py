from __future__ import annotations

import json
from dataclasses import dataclass, fields
from typing import Optional

import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import CubicSpline

from holytools.abstract import Serializable
from xrdpattern.xrd.experiment import PowderExperiment

# -------------------------------------------

@dataclass
class PatternData(Serializable):
    two_theta_values : NDArray
    intensities : NDArray
    label : PowderExperiment
    name : Optional[str] = None

    @classmethod
    def make_unlabeled(cls, two_theta_values: list[float], intensities: list[float]) -> PatternData:
        metadata = PowderExperiment.make_empty()
        two_theta_values, intensities = np.array(two_theta_values), np.array(intensities)
        return cls(two_theta_values=two_theta_values, intensities=intensities, label=metadata)

    def to_dict(self):
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def get_standardized_map(self, start_val : float, stop_val : float, num_entries : int) -> (list[float], list[float]):
        start, end = self.two_theta_values[0], self.two_theta_values[-1]
        std_angles = np.linspace(start=start_val, stop=stop_val, num=num_entries)

        x = np.array(self.two_theta_values)
        y = np.array(self.intensities)
        y -= np.min(y)

        cs = CubicSpline(x, y)
        mask = (std_angles >= start) & (std_angles <= end)
        std_intensities = cs(std_angles)
        std_intensities = std_intensities * mask

        max_intensity = np.max(std_intensities)
        normalization_factor = max_intensity if max_intensity > 0 else 1
        std_intensities = std_intensities/normalization_factor

        return std_angles, std_intensities

    def to_str(self) -> str:
        the_dict = {'two_theta_values' : self.two_theta_values.tolist(),
                    'intensities' : self.intensities.tolist(),
                    'label' : self.label.to_str(),
                    'name' : str(self.name)}

        return json.dumps(the_dict)

    @classmethod
    def from_str(cls, json_str: str) -> PatternData:
        data = json.loads(json_str)
        two_theta_values = np.array(data['two_theta_values'])
        intensities = np.array(data['intensities'])
        label = PowderExperiment.from_str(data['label'])
        name = data['name']
        return cls(two_theta_values=two_theta_values, intensities=intensities, label=label, name=name)


    def __eq__(self, other : PatternData):
        if not isinstance(other, PatternData):
            return False

        angles_equal = np.array_equal(self.two_theta_values, other.two_theta_values)
        intensities_equal = np.array_equal(self.intensities, other.intensities)
        labels_equal = self.label.list_repr = other.label.list_repr

        return angles_equal and intensities_equal and labels_equal


if __name__ == '__main__':
    pass