from __future__ import annotations

import math
from dataclasses import dataclass, field
from importlib.metadata import version
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

    def is_nonempty(self) -> bool:
        xray_info_nonemtpy = not self.xray_info.primary_wavelength is None or not self.xray_info.secondary_wavelength is None
        if len(self.phases) == 0:
            return xray_info_nonemtpy

        primary_phase = self.phases[0]
        composition_nonempty = primary_phase.chemical_composition

        a,b,c = primary_phase.lengths
        alpha, beta, gamma = primary_phase.angles
        lattice_params_nonempty = not all(math.isnan(x) for x in [a, b, c, alpha, beta, gamma])
        crystal_basis_nonempty = len(primary_phase.basis) > 0
        return xray_info_nonemtpy or composition_nonempty or lattice_params_nonempty or crystal_basis_nonempty

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
            'lengths': to_tensor(self.phases[0].lengths),
            'angles' : to_tensor(self.phases[0].angles),
            'spg_probabilities' : to_tensor(spg_list),
            'crystallite_size' : to_tensor(self.crystallite_size_nm) if self.crystallite_size_nm else None,
            'temperature' : to_tensor(self.temp_K) if self.temp_K else None,
            'primary_wavelength' : to_tensor(self.xray_info.primary_wavelength) if self.xray_info.primary_wavelength else None,
            'secondary_wavelength' : to_tensor(self.xray_info.secondary_wavelength) if self.xray_info.secondary_wavelength else None,
        }
        td = ExperimentTensor(feature_dict)
        return td


@dataclass
class Metadata(JsonDataclass):
    filename: Optional[str] = None
    institution: Optional[str] = None
    contributor_name: Optional[str] = None
    original_file_format: Optional[str] = None
    measurement_date: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    xrdpattern_version: str = field(default_factory=lambda: get_library_version('xrdpattern'))

    def __eq__(self, other : Metadata):
        s1, s2 = self.to_str(), other.to_str()
        return s1 == s2

    def remove_filename(self):
        self.filename = None


class ExperimentTensor(TensorDict):
    def get_lattice_params(self):
        lengths, angles = self.get('lengths'), self.get('angles')
        return torch.cat([lengths, angles], dim=0)

    def get_spg_probabilities(self):
        return self.get('spg_probabilities')

    def get_crystallite_size(self):
        return self.get('crystallite_size')

    def get_ambient_temperature(self):
        return self.get('temperature')

    def get_primary_wavelength(self):
        return self.get('primary_wavelength')

    def get_secondary_wavelength(self):
        return self.get('secondary_wavelength')


def get_library_version(library_name : str):
    return version(library_name)
