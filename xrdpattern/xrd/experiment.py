from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import torch
from tensordict import TensorDict
from torch import Tensor

from holytools.abstract import JsonDataclass
from xrdpattern.crystal import CrystalPhase, CrystalBase, AtomicSite
from xrdpattern.xrd.xray import XRayInfo

NUM_SPACEGROUPS = 230
MAX_ATOMIC_SITES = 100

# ---------------------------------------------------------

@dataclass
class PowderExperiment(JsonDataclass):
    phases: list[CrystalPhase]
    xray_info : XRayInfo
    is_simulated : bool = False
    crystallite_size: Optional[float] = None
    temp_in_celcius: Optional[float] = None

    def __post_init__(self):
        if len(self.phases) == 0:
            raise ValueError(f'Material must have at least one phase! Got {len(self.phases)}')

        if len(self.phases) == 1:
            self.phases[0].phase_fraction = 1

    @classmethod
    def make_empty(cls, is_simulated : bool = False, num_phases : int = 1) -> PowderExperiment:
        phases = []
        for j in range(num_phases):
            lengths = (float('nan'),float('nan'), float('nan'))
            angles = (float('nan'),float('nan'), float('nan'))
            base = CrystalBase()

            p = CrystalPhase(lengths=lengths, angles=angles, base=base)
            phases.append(p)

        xray_info = XRayInfo.mk_empty()
        return cls(phases=phases, crystallite_size=None, temp_in_celcius=None, xray_info=xray_info, is_simulated=is_simulated)

    @classmethod
    def from_multi_phase(cls, phases : list[CrystalPhase]):
        return cls(phases=phases, crystallite_size=None, xray_info=XRayInfo.mk_empty(), is_simulated=False)

    @classmethod
    def from_single_phase(cls, phase : CrystalPhase, crystallite_size : Optional[float] = None, is_simulated : bool = False):
        artifacts = XRayInfo.mk_empty()
        return cls(phases=[phase], crystallite_size=crystallite_size, xray_info=artifacts, is_simulated=is_simulated)

    @classmethod
    def from_cif(cls, cif_content : str) -> PowderExperiment:
        structure = CrystalPhase.from_cif(cif_content)
        structure.calculate_properties()

        xray_info = XRayInfo.mk_empty()
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
        xray_info_nonemtpy = self.xray_info.primary_wavelength or self.xray_info.secondary_wavelength
        
        primary_phase = self.primary_phase
        composition_nonempty = primary_phase.chemical_composition

        a,b,c = primary_phase.lengths
        alpha, beta, gamma = primary_phase.angles
        lattice_params_nonempty = not all(math.isnan(x) for x in [a, b, c, alpha, beta, gamma])
        crystal_basis_nonempty = len(primary_phase.base) > 0
        # print(f'lattiice params, crystal basis, xray info = {lattice_params_nonempty, crystal_basis_nonempty, xray_info_nonemtpy}')
        
        return xray_info_nonemtpy or composition_nonempty or lattice_params_nonempty or crystal_basis_nonempty

    @property
    def primary_phase(self) -> CrystalPhase:
        return self.phases[0]

    @property
    def primary_wavelength(self) -> float:
        return self.xray_info.primary_wavelength

    @property
    def secondary_wavelength(self) -> float:
        return self.xray_info.secondary_wavelength

    def get_list_repr(self) -> list:
        list_repr = []
        structure = self.primary_phase

        a, b, c = structure.lengths
        alpha, beta, gamma = structure.angles
        lattice_params = [a, b, c, alpha, beta, gamma]
        list_repr += lattice_params

        base = structure.base
        padded_base = self.get_padded_base(base=base, nan_padding=base.is_empty())
        for atomic_site in padded_base:
            list_repr += atomic_site.as_list()

        if structure.spacegroup is None:
            spg_logits_list = [float('nan') for _ in range(NUM_SPACEGROUPS)]
        else:
            spg_logits_list = [1000 if j + 1 == structure.spacegroup else 0 for j in range(NUM_SPACEGROUPS)]
        list_repr += spg_logits_list

        list_repr += self.xray_info.as_list()
        list_repr += [self.is_simulated]

        return list_repr

    @staticmethod
    def get_padded_base(base: CrystalBase, nan_padding : bool) -> CrystalBase:
        def make_padding_site():
            if nan_padding:
                site = AtomicSite.make_placeholder()
            else:
                site = AtomicSite.make_void()
            return site

        delta = MAX_ATOMIC_SITES - len(base)
        if delta < 0:
            raise ValueError(f'Base is too large! Size = {len(base)} exceeds MAX_ATOMIC_SITES = {MAX_ATOMIC_SITES}')

        padded_base = base + [make_padding_site() for _ in range(delta)]
        return padded_base


    def to_tensor(self, dtype : torch.dtype = torch.get_default_dtype(), device : torch.device = torch.get_default_device()) -> LabelTensor:
        tensor = torch.tensor(self.get_list_repr(), dtype=dtype, device=device)
        return LabelTensor(tensor)


class LabelType(Enum):
    spg = "spg"
    lattice = "lattice"
    atom_coords = "atom_coords"
    composition = "composition"

class LabelTensor(TensorDict):
    def get_lattice_params(self) -> Tensor:
        return self['lattice_params']

    def get_atomic_site(self, index : int) -> Tensor:
        return self[f'atomic_site_{index}']

    def get_spg_logits(self) -> Tensor:
        return self['spg_logits']

    def get_spg_probabilities(self) -> Tensor:
        logits = self.get_spg_logits()
        return torch.softmax(logits, dim=-1)

    def get_artifacts(self) -> LabelTensor:
        return self['artifacts']

    def get_simulated_probability(self) -> LabelTensor:
        return self['is_simulated']

    # noinspection PyTypeChecker
    def to_sample(self) -> PowderExperiment:
        raise NotImplementedError


