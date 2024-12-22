from __future__ import annotations

import json
import math
from dataclasses import dataclass, fields, field
from enum import Enum

import numpy as np
from numpy.typing import NDArray
from orjson import orjson

from holytools.abstract import Serializable
from xrdpattern.crystal import CrystalPhase
from xrdpattern.xrd.experiment import PowderExperiment
from xrdpattern.xrd import Metadata

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

    def get_phase(self, phase_num : int) -> CrystalPhase:
        return self.powder_experiment.phases[phase_num]

    def has_label(self, label_type: LabelType) -> bool:
        if label_type == LabelType.composition:
            return self.primary_phase.chemical_composition is not None
        if label_type == LabelType.lattice:
            return all(not math.isnan(x) for x in self.primary_phase.lengths) and all(not math.isnan(x) for x in self.primary_phase.angles)
        if label_type == LabelType.atom_coords:
            return len(self.primary_phase.base) > 0
        if label_type == LabelType.spg:
            spg_explicit = self.primary_phase.spacegroup is not None
            spg_implicit = self.has_label(label_type=LabelType.lattice) and self.has_label(
                label_type=LabelType.atom_coords)
            return spg_explicit or spg_implicit
        return False

    def is_labeled(self) -> bool:
        return any(self.has_label(label_type=lt) for lt in LabelType)

    @property
    def num_entries(self) -> int:
        return len(self.two_theta_values)

    @property
    def primary_phase(self) -> CrystalPhase:
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

    @property
    def composition(self) -> str:
        comp = ''
        for phase in self.powder_experiment.phases:
            comp += phase.chemical_composition
        return comp



class LabelType(Enum):
    spg = "spg"
    lattice = "lattice"
    atom_coords = "atom_coords"
    composition = "composition"