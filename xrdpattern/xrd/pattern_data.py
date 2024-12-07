from __future__ import annotations

import json
import math
from dataclasses import dataclass, fields, field

import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import CubicSpline

from holytools.abstract import Serializable

from xrdpattern.crystal import CrystalPhase
from xrdpattern.xrd import XRayInfo
from xrdpattern.xrd.metadata import Metadata
from xrdpattern.xrd.experiment import PowderExperiment, LabelType


# -------------------------------------------

@dataclass
class XrdPatternData(Serializable):
    two_theta_values : NDArray
    intensities : NDArray
    powder_experiment : PowderExperiment
    metadata: Metadata = field(default_factory=Metadata)

    def __post_init__(self):
        if len(self.two_theta_values) != len(self.intensities):
            raise ValueError(f'Two theta values and intensities must have the same length. Got lengths: {len(self.two_theta_values)}, {len(self.intensities)}')
        if len(self.two_theta_values) < 50:
            raise ValueError(f'Data is too short. Less than 50 entries! Two theta values = {self.two_theta_values}')
        _, unique_indices = np.unique(self.two_theta_values, return_index=True)
        if len(unique_indices) == 1:
            raise ValueError(f'Pattern contains only one unique value. Two theta values = {self.two_theta_values[:20]}...')
        if np.isnan(self.two_theta_values).any() or np.isnan(self.intensities).any():
            raise ValueError(f'TwoThetaValues or Intensities contain NaN values')
        if np.all(self.intensities == 0):
            raise ValueError(f'All intensities are zero')


    @classmethod
    def make_unlabeled(cls, two_theta_values: list[float], intensities: list[float]) -> XrdPatternData:
        metadata = PowderExperiment.make_empty()
        two_theta_values, intensities = np.array(two_theta_values), np.array(intensities)
        return cls(two_theta_values=two_theta_values, intensities=intensities, powder_experiment=metadata)

    def to_dict(self):
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def _get_uniform(self, start_val : float, stop_val : float, num_entries : int, constant_padding : bool) -> (list[float], list[float]):
        start, end = self.two_theta_values[0], self.two_theta_values[-1]
        std_angles = np.linspace(start=start_val, stop=stop_val, num=num_entries)

        x = np.array(self.two_theta_values)
        y = np.array(self.intensities)
        x, y = self.to_strictly_increasing(x, y)
        y -= np.min(y)

        cs = CubicSpline(x, y)
        std_intensities = cs(std_angles)
        below_start_indices = np.where(std_angles < start)[0]
        above_end_indices = np.where(std_angles > end)[0]

        if constant_padding:
            below_start, after_end = y[0], y[-1]
        else:
            below_start, after_end = 0, 0

        std_intensities[below_start_indices] = below_start
        std_intensities[above_end_indices] = after_end

        std_intensities -= np.min(std_intensities)
        max_intensity = np.max(std_intensities)
        normalization_factor = max_intensity if max_intensity > 0 else 1
        std_intensities = std_intensities/normalization_factor

        return std_angles, std_intensities

    @staticmethod
    def to_strictly_increasing(x : NDArray, y : NDArray):
        indices = np.argsort(x)
        x_sorted, y_sorted = x[indices], y[indices]
        _, unique_indices = np.unique(x_sorted, return_index=True)
        x = x_sorted[unique_indices]
        y = y_sorted[unique_indices]

        return x, y


    def to_str(self) -> str:
        the_dict = {'two_theta_values' : self.two_theta_values.tolist(),
                    'intensities' : self.intensities.tolist(),
                    'label' : self.powder_experiment.to_str(),
                    'metadata' : self.metadata.to_str()}

        return json.dumps(the_dict)

    @classmethod
    def from_str(cls, json_str: str) -> XrdPatternData:
        data = json.loads(json_str)
        two_theta_values = np.array(data['two_theta_values'])
        intensities = np.array(data['intensities'])
        label = PowderExperiment.from_str(data['label'])
        metadata = Metadata.from_str(data['metadata'])

        return cls(two_theta_values=two_theta_values, intensities=intensities, powder_experiment=label, metadata=metadata)


    # ---------------------------------------
    # properties

    def get_name(self) -> str:
        name = self.metadata.filename
        if not name:
            name = f'unnamed_pattern'

        return name

    def get_phase(self, phase_num : int) -> CrystalPhase:
        return self.powder_experiment.phases[phase_num]

    @property
    def num_entries(self) -> int:
        return len(self.two_theta_values)

    @property
    def primary_phase(self) -> CrystalPhase:
        return self.powder_experiment.primary_phase

    @property
    def startval(self):
        return self.two_theta_values[0]

    @property
    def endval(self):
        return self.two_theta_values[-1]

    @property
    def xray_info(self) -> XRayInfo:
        return self.powder_experiment.xray_info

    @property
    def is_simulated(self) -> bool:
        return self.powder_experiment.is_simulated

    def has_label(self, label_type: LabelType) -> bool:
        if label_type == LabelType.composition:
            return self.primary_phase.chemical_composition is not None
        if label_type == LabelType.spg:
            return self.primary_phase.spacegroup is not None
        if label_type == LabelType.lattice:
            return all(not math.isnan(x) for x in self.primary_phase.lengths) and all(not math.isnan(x) for x in self.primary_phase.angles)
        if label_type == LabelType.atom_coords:
            return len(self.primary_phase.base) > 0
        return False

    def __eq__(self, other : XrdPatternData):
        for attr in fields(self):
            v1, v2 = getattr(self, attr.name), getattr(other, attr.name)
            if isinstance(v1, np.ndarray):
                is_ok = np.array_equal(v1, v2)
            elif isinstance(v1, PowderExperiment):
                objs_equal = [str(x)==str(y) for x,y in zip(v1.get_list_repr(), v2.get_list_repr())]
                is_ok = all(objs_equal)
            else:
                is_ok = v1 == v2

            if not is_ok:
                return False

        return True


if __name__ == '__main__':
    pass