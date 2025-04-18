from __future__ import annotations

import json
from dataclasses import dataclass, field
from dataclasses import fields

import numpy as np
from numpy.typing import NDArray
from orjson import orjson

from xrdpattern.crystal import CrystalStructure
from xrdpattern.serialization import Serializable
from xrdpattern.xrd.experiment import PowderExperiment
from xrdpattern.xrd.metadata import Metadata


# -------------------------------------------

@dataclass
class XrdData(Serializable):
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
        if np.isinf(self.two_theta_values).any() or np.isinf(self.intensities).any():
            raise ValueError(f'TwoThetaValues or Intensities contain Inf values')
        if np.all(self.intensities == 0):
            raise ValueError(f'All intensities are zero')
        if np.any(self.two_theta_values < 0):
            raise ValueError(f'TwoThetaValues contain negative values')

    @classmethod
    def make_unlabeled(cls, two_theta_values: list[float], intensities: list[float]) -> XrdData:
        metadata = PowderExperiment.make_empty()
        two_theta_values, intensities = np.array(two_theta_values), np.array(intensities)
        return cls(two_theta_values=two_theta_values, intensities=intensities, powder_experiment=metadata)

    @classmethod
    def from_str(cls, json_str: str) -> XrdData:
        data = orjson.loads(json_str)
        two_theta_values = np.array(data['two_theta_values'])
        intensities = np.array(data['intensities'])
        label = PowderExperiment.from_str(data['label'])
        metadata = Metadata.from_str(data['metadata'])

        return cls(two_theta_values=two_theta_values, intensities=intensities, powder_experiment=label, metadata=metadata)

    def to_str(self) -> str:
        the_dict = {'two_theta_values' : self.two_theta_values.tolist(),
                    'intensities' : self.intensities.tolist(),
                    'label' : self.powder_experiment.to_str(),
                    'metadata' : self.metadata.to_str()}

        return json.dumps(the_dict)

    def to_init_dict(self):
        return {f.name: getattr(self, f.name) for f in fields(self)}

    # ---------------------------------------
    # properties

    def get_name(self) -> str:
        name = self.metadata.filename
        if not name:
            name = self.primary_phase.chemical_composition
        if not name:
            name = f'unnamed_pattern'

        return name

    def get_phase(self, phase_num : int) -> CrystalStructure:
        return self.powder_experiment.phases[phase_num]

    @property
    def num_entries(self) -> int:
        return len(self.two_theta_values)

    @property
    def primary_phase(self) -> CrystalStructure:
        return self.powder_experiment.phases[0]

    @property
    def startval(self):
        return min(self.two_theta_values)

    @property
    def endval(self):
        return max(self.two_theta_values)

    @property
    def angular_resolution(self):
        return (self.endval-self.startval)/self.num_entries

    @property
    def is_simulated(self) -> bool:
        return self.powder_experiment.is_simulated
