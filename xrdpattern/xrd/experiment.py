from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import torch
from tensordict import TensorDict
from torch import Tensor

from holytools.abstract import JsonDataclass
from xrdpattern.crystal import CrystalStructure, CrystalBase, AtomicSite, Angles, Lengths
from xrdpattern.xrd.xray import XRayInfo

NUM_SPACEGROUPS = 230
MAX_ATOMIC_SITES = 100

# ---------------------------------------------------------

@dataclass
class PowderExperiment(JsonDataclass):
    powder : PowderSample
    artifacts : XRayInfo
    is_simulated : bool

    @classmethod
    def make_empty(cls, is_simulated : bool = False) -> PowderExperiment:
        lengths = Lengths(a=None, b=None, c=None)
        angles = Angles(alpha=None, beta=None, gamma=None)
        base = CrystalBase()

        structure = CrystalStructure(lengths=lengths, angles=angles, base=base)
        sample = PowderSample(crystal_structure=structure,crystallite_size=None, temp_in_celcius=None)
        artifacts = XRayInfo.mk_empty()

        return cls(sample, artifacts, is_simulated=is_simulated)

    @classmethod
    def from_structure(cls, structure : CrystalStructure, crystallite_size : float, is_simulated : bool):
        powder = PowderSample(crystal_structure=structure, crystallite_size=crystallite_size)
        artifacts = XRayInfo.mk_empty()
        return cls(powder=powder, artifacts=artifacts, is_simulated=is_simulated)


    def get_list_repr(self) -> list:
        list_repr = []
        structure = self.crystal_structure

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

        list_repr += self.artifacts.as_list()
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

    # ---------------------------------------------------------
    # properties

    def is_partially_labeled(self) -> bool:
        powder_tensor = torch.tensor(self.get_list_repr())
        is_nan = powder_tensor != powder_tensor
        print(f'Powder tensor len = {len(powder_tensor)}')
        print(f'Nanvalues, non-nan values = {is_nan.sum()}, {is_nan.numel() - is_nan.sum()}')

        return any(is_nan.tolist())

    @property
    def crystallite_size(self) -> float:
        return self.powder.crystallite_size

    @property
    def temp_in_celcius(self) -> float:
        return self.powder.temp_in_celcius

    @property
    def crystal_structure(self) -> CrystalStructure:
        return self.powder.crystal_structure

    @property
    def domain(self) -> bool:
        return self.is_simulated

    @property
    def primary_wavelength(self) -> float:
        return self.artifacts.primary_wavelength

    @property
    def secondary_wavelength(self) -> float:
        return self.artifacts.secondary_wavelength

    # ---------------------------------------------------------
    # save/load

    @classmethod
    def from_cif(cls, cif_content : str) -> PowderExperiment:
        structure = CrystalStructure.from_cif(cif_content)
        powder = PowderSample(crystal_structure=structure)
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

        return cls(powder=powder, artifacts=xray_info, is_simulated=False)



@dataclass
class PowderSample(JsonDataclass):
    crystal_structure: CrystalStructure
    crystallite_size: Optional[float] = None
    temp_in_celcius : Optional[float] = None
    shape_factor : Optional[float] = 0.9


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
