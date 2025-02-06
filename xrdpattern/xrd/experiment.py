from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from importlib.metadata import version
from typing import Optional

import torch

from holytools.abstract import JsonDataclass
from xrdpattern.crystal import CrystalPhase, CrystalBase, AtomicSite
from xrdpattern.xrd.tensorization import LabelTensor

NUM_SPACEGROUPS = 230
MAX_ATOMIC_SITES = 100

# ---------------------------------------------------------

@dataclass
class PowderExperiment(JsonDataclass):
    phases: list[CrystalPhase]
    xray_info : XrayInfo
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

        xray_info = XrayInfo.mk_empty()
        return cls(phases=phases, crystallite_size=None, temp_in_celcius=None, xray_info=xray_info, is_simulated=is_simulated)

    @classmethod
    def from_multi_phase(cls, phases : list[CrystalPhase]):
        return cls(phases=phases, crystallite_size=None, xray_info=XrayInfo.mk_empty(), is_simulated=False)

    @classmethod
    def from_single_phase(cls, phase : CrystalPhase, crystallite_size : Optional[float] = None, is_simulated : bool = False):
        artifacts = XrayInfo.mk_empty()
        return cls(phases=[phase], crystallite_size=crystallite_size, xray_info=artifacts, is_simulated=is_simulated)

    @classmethod
    def from_cif(cls, cif_content : str) -> PowderExperiment:
        structure = CrystalPhase.from_cif(cif_content)
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
        xray_info_nonemtpy = self.xray_info.primary_wavelength or self.xray_info.secondary_wavelength
        
        primary_phase = self.phases[0]
        composition_nonempty = primary_phase.chemical_composition

        a,b,c = primary_phase.lengths
        alpha, beta, gamma = primary_phase.angles
        lattice_params_nonempty = not all(math.isnan(x) for x in [a, b, c, alpha, beta, gamma])
        crystal_basis_nonempty = len(primary_phase.base) > 0
        return xray_info_nonemtpy or composition_nonempty or lattice_params_nonempty or crystal_basis_nonempty

    @property
    def primary_wavelength(self) -> float:
        return self.xray_info.primary_wavelength

    @property
    def secondary_wavelength(self) -> float:
        return self.xray_info.secondary_wavelength

    def get_list_repr(self) -> list:
        list_repr = []
        structure = self.phases[0]

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


@dataclass
class XrayInfo(JsonDataclass):
    primary_wavelength: Optional[float]
    secondary_wavelength: Optional[float]

    @classmethod
    def mk_empty(cls):
        return cls(primary_wavelength=None, secondary_wavelength=None)

    def as_list(self) -> list[float]:
        return [self.primary_wavelength, self.secondary_wavelength]

    @staticmethod
    def default_ratio() -> float:
        return 0.5


class XrdAnode(Enum):
    Cu = "Cu"
    Mo = "Mo"
    Cr = "Cr"
    Fe = "Fe"
    Co = "Co"
    Ag = "Ag"

    def get_wavelengths(self) -> (float, float):
        MATERiAL_TO_WAVELENGTHS = {
            "Cu": (1.54439, 1.54056),
            "Mo": (0.71359, 0.70930),
            "Cr": (2.29361, 2.28970),
            "Fe": (1.93998, 1.93604),
            "Co": (1.79285, 1.78896),
            "Ag": (0.563813, 0.559421),
        }
        return MATERiAL_TO_WAVELENGTHS[self.value]

    def get_xray_info(self) -> XrayInfo:
        primary, secondary = self.get_wavelengths()
        return XrayInfo(primary_wavelength=primary, secondary_wavelength=secondary)


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

def get_library_version(library_name : str):
    return version(library_name)
