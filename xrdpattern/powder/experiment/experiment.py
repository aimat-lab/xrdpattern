from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Tuple, Optional

import torch
from xrdpattern.powder.structure import CrystalStructure, CrystalBase, AtomicSite
from xrdpattern.powder.structure import Angles, Lengths
from .sample_properties import SampleProperties, Artifacts

# ---------------------------------------------------------

NUM_SPACEGROUPS = 230
NUM_ATOMIC_SITES = 100

@dataclass
class QuantityRegion:
    obj : list
    start : int
    end : int

    def get_size(self) -> int:
        return self.end + 1 - self.start


@dataclass
class PatternLabel:
    powder : SampleProperties
    artifacts : Artifacts
    is_simulated : bool

    def __post_init__(self):
        self.list_repr = []
        structure = self.crystal_structure

        a, b, c = structure.lengths
        alpha, beta, gamma = structure.angles
        lattice_params = [a, b, c, alpha, beta, gamma]
        self.lattice_param_region : QuantityRegion = self.add_region_quantity(list_obj=lattice_params)

        self.atomic_site_regions : list[QuantityRegion] = []
        base = structure.base
        padded_base = self.get_padded_base(base=base, nan_padding=base.is_empty())
        for atomic_site in padded_base:
            region_obj = self.add_region_quantity(list_obj=atomic_site.as_list())
            self.atomic_site_regions.append(region_obj)

        if structure.space_group is None:
            spacegroup_list = [float('nan') for _ in range(NUM_SPACEGROUPS)]
        else:
            spacegroup_list = [j + 1 == structure.space_group for j in range(NUM_SPACEGROUPS)]
        self.spacegroup_region : QuantityRegion = self.add_region_quantity(list_obj=spacegroup_list)

        artifacts_list = self.artifacts.as_list()
        self.artifacts_region : QuantityRegion = self.add_region_quantity(artifacts_list)

        domain_list = [self.is_simulated]
        self.domain_region : QuantityRegion = self.add_region_quantity(domain_list)


    def add_region_quantity(self, list_obj : list) -> QuantityRegion:
        current_len = len(self.list_repr)
        region = QuantityRegion(obj=list_obj, start=current_len, end=current_len + len(list_obj))
        self.list_repr += list_obj
        return region


    @staticmethod
    def get_padded_base(base: CrystalBase, nan_padding : bool) -> CrystalBase:
        if len(base) > NUM_ATOMIC_SITES:
            raise ValueError(f"Too many atomic sites in base: {len(base)}")

        def make_padding_site():
            if nan_padding:
                site = AtomicSite.make_placeholder()
            else:
                site = AtomicSite.make_void()
            return site

        delta = NUM_ATOMIC_SITES - len(base)
        padded_base = base + [make_padding_site() for _ in range(delta)]
        return padded_base


    @classmethod
    def make_empty(cls) -> PatternLabel:
        lengths = Lengths(a=torch.nan, b=torch.nan, c=torch.nan)
        angles= Angles(alpha=torch.nan, beta=torch.nan, gamma=torch.nan)
        base = CrystalBase()

        structure = CrystalStructure(lengths=lengths, angles=angles, base=base)
        print(f'Empty crystal structure spacegroups = {structure.space_group}')
        sample = SampleProperties(crystallite_size=torch.nan, crystal_structure=structure)
        artifacts = Artifacts(primary_wavelength=torch.nan,
                              secondary_wavelength=torch.nan,
                              secondary_to_primary=torch.nan,
                              shape_factor=torch.nan)

        return cls(sample, artifacts, is_simulated=False)


    def is_partial_label(self) -> bool:
        powder_tensor = torch.tensor(self.list_repr)
        is_nan = powder_tensor != powder_tensor
        print(f'Powder tensor len = {len(powder_tensor)}')
        print(f'Nanvalues, non-nan values = {is_nan.sum()}, {is_nan.numel() - is_nan.sum()}')

        return any(is_nan.tolist())

    # ---------------------------------------------------------
    # properties

    @property
    def crystallite_size(self) -> float:
        return self.powder.crystallite_size

    @property
    def temp_in_celcius(self) -> float:
        return self.powder.temp_in_kelvin

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


