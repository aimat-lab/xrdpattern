from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import torch
from tensordict import TensorDict

from xrdpattern.crystal import CrystalStructure
from xrdpattern.serialization import JsonDataclass
from xrdpattern.xrd.xray import XrayInfo

NUM_SPACEGROUPS = 230
MAX_ATOMIC_SITES = 100

# ---------------------------------------------------------

@dataclass
class PowderExperiment(JsonDataclass):
    phases: list[CrystalStructure]
    xray_info : XrayInfo
    is_simulated : bool = False
    crystallite_size_nm: Optional[float] = None
    temp_K: Optional[float] = None

    def __post_init__(self):
        if len(self.phases) == 1:
            self.phases[0].phase_fraction = 1

    @classmethod
    def make_empty(cls, is_simulated: bool = False) -> PowderExperiment:
        xray_info = XrayInfo.mk_empty()
        return cls(phases=[], xray_info=xray_info, is_simulated=is_simulated)

    @classmethod
    def from_multi_phase(cls, phases : list[CrystalStructure]):
        return cls(phases=phases, crystallite_size_nm=None, xray_info=XrayInfo.mk_empty(), is_simulated=False)

    @classmethod
    def from_single_phase(cls, phase : CrystalStructure, crystallite_size : Optional[float] = None, is_simulated : bool = False):
        artifacts = XrayInfo.mk_empty()
        return cls(phases=[phase], crystallite_size_nm=crystallite_size, xray_info=artifacts, is_simulated=is_simulated)

    @classmethod
    def from_cif(cls, cif_content : str) -> PowderExperiment:
        structure = CrystalStructure.from_cif(cif_content)
        structure.calculate_properties()

        xray_info = XrayInfo.mk_empty()
        lines = cif_content.split('\n')
        for l in lines:
            if '_diffrn_radiation_wavelength' in l:
                parts = l.split()
                if len(parts) > 1:
                    xray_info.primary_wavelength = float(parts[-1])

        blocks = cif_content.split(f'loop_')
        for b in blocks:
            if '_diffrn_radiation_wavelength_wt' in b:
                b = b.strip()
                b_lines = b.split('\n')
                xray_info.primary_wavelength = float(b_lines[-2].split()[0])
                xray_info.secondary_wavelength = float(b_lines[-1].split()[0])

        return cls(phases=[structure], xray_info=xray_info, is_simulated=False)

    # ---------------------------------------------------------
    # properties

    @property
    def primary_phase(self):
        return self.phases[0]

    def has_label(self, label_type: LabelType) -> bool:
        if label_type == LabelType.primary_wavelength:
            return not self.xray_info.primary_wavelength is None
        if label_type == LabelType.secondary_wavelength:
            return not self.xray_info.secondary_wavelength is None

        if len(self.phases) == 0:
            return False

        if label_type == LabelType.lattice:
            return True
        elif label_type == LabelType.spg:
            return self.primary_phase.spacegroup is not None
        elif label_type == LabelType.composition:
            return self.primary_phase.chemical_composition is not None
        elif label_type == LabelType.temperature:
            return self.temp_K is not None
        elif label_type == LabelType.crystallite_size:
            return self.crystallite_size_nm is not None
        elif label_type == LabelType.atom_coords:
            return len(self.primary_phase.basis.atom_sites) > 0
        else:
            raise ValueError(f'Label type {label_type} is not supported.')

    def is_labeled(self) -> bool:
        return any(self.has_label(label_type=lt) for lt in LabelType)

    def __eq__(self, other : PowderExperiment):
        return self.to_str() == other.to_str()

    def to_tensordict(self, dtype : torch.dtype = torch.get_default_dtype(),
                            device : torch.device = torch.get_default_device()) -> ExperimentTensor:

        def to_tensor(data):
            return torch.tensor(data=data, dtype=dtype, device=device)

        if len(self.phases) == 0:
            raise ValueError('No phases in the experiment. Cannot convert to TensorDict.')

        spg_list = [self.phases[0].spacegroup == j for j in range(1,NUM_SPACEGROUPS+1)]
        feature_dict = {
            LabelType.lengths.value: to_tensor(self.phases[0].lengths),
            LabelType.angles.value : to_tensor(self.phases[0].angles),
            LabelType.spg.value : to_tensor(spg_list),
            LabelType.crystallite_size.value : to_tensor(self.crystallite_size_nm) if self.crystallite_size_nm else None,
            LabelType.temperature.value : to_tensor(self.temp_K) if self.temp_K else None,
            LabelType.primary_wavelength.value : to_tensor(self.xray_info.primary_wavelength) if self.xray_info.primary_wavelength else None,
            LabelType.secondary_wavelength.value : to_tensor(self.xray_info.secondary_wavelength) if self.xray_info.secondary_wavelength else None,
        }
        td = ExperimentTensor(feature_dict)
        return td


class ExperimentTensor(TensorDict):
    def get_lattice_params(self):
        lengths, angles = self.get('lengths'), self.get('angles')
        return torch.cat([lengths, angles], dim=0)

    def get_spg_probabilities(self):
        return self.get(LabelType.spg.value)

    def get_crystallite_size(self):
        return self.get(LabelType.crystallite_size.value)

    def get_ambient_temperature(self):
        return self.get(LabelType.temperature.value)

    def get_primary_wavelength(self):
        return self.get(LabelType.primary_wavelength.value)

    def get_secondary_wavelength(self):
        return self.get(LabelType.secondary_wavelength.value)


class LabelType(Enum):
    lattice = "lattice"
    lengths = "lengths"
    angles = "angles"
    atom_coords = "atom_coords"
    spg = "spg"
    crystallite_size = 'crystallite_size'
    temperature = 'temperature'
    primary_wavelength = 'primary_wavelength'
    secondary_wavelength = 'secondary_wavelength'
    composition = "composition"


