from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Tuple, Optional

from torch import Tensor

from xrdpattern.powder.structure import CrystalStructure, CrystalBase, AtomicSite
from .powder import Powder, Artifacts

from xrdpattern.powder.structure import Angles, Lengths

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
class PowderExperiment:
    powder : Powder
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


    @classmethod
    def from_xylib_header(cls, header_str: str) -> PowderExperiment:
        metadata_map = cls.get_key_value_dict(header_str=header_str)

        def get_float(key: str) -> Optional[float]:
            val = metadata_map.get(key)
            if val:
                val = float(val)
            return val

        experiment = cls.make_empty()
        experiment.artifacts = Artifacts(
            primary_wavelength=get_float('ALPHA1'),
            secondary_wavelength=get_float('ALPHA2'),
            secondary_to_primary=get_float('ALPHA_RATIO')
        )
        experiment.powder.temp_in_kelvin = get_float('TEMP_CELCIUS') + 273.15

        return experiment

    @classmethod
    def get_key_value_dict(cls, header_str: str) -> dict:
        key_value_dict = {}
        for key, value in cls.get_key_value_pairs(header_str):
            key_value_dict[key] = value
        return key_value_dict

    @staticmethod
    def get_key_value_pairs(header_str: str) -> Iterator[Tuple[str, str]]:
        commented_lines = [line for line in header_str.splitlines() if line.startswith('#')]
        for line in commented_lines:
            key_value = line[1:].split(':', 1)
            if len(key_value) == 2:
                yield key_value[0].strip(), key_value[1].strip()

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
    def make_empty(cls) -> PowderExperiment:
        lengths = Lengths(a=torch.nan, b=torch.nan, c=torch.nan)
        angles= Angles(alpha=torch.nan, beta=torch.nan, gamma=torch.nan)
        base = CrystalBase()

        structure = CrystalStructure(lengths=lengths, angles=angles, base=base)
        print(f'Empty crystal structure spacegroups = {structure.space_group}')
        sample = Powder(crystallite_size=torch.nan, crystal_structure=structure)
        artifacts = Artifacts(primary_wavelength=torch.nan,
                              secondary_wavelength=torch.nan,
                              secondary_to_primary=torch.nan,
                              shape_factor=torch.nan)

        return cls(sample, artifacts, is_simulated=False)


    def is_partial_label(self) -> bool:
        powder_tensor = self.to_tensor()
        is_nan = powder_tensor != powder_tensor
        print(f'Powder tensor len = {len(powder_tensor)}')
        print(f'Nanvalues, non-nan values = {is_nan.sum()}, {is_nan.numel() - is_nan.sum()}')

        return any(is_nan.tolist())


    # ---------------------------------------------------------
    # torch

    def to_tensor(self) -> PowderTensor:
        tensor = Tensor(self.list_repr)
        return PowderTensor(tensor)

    @classmethod
    def from_tensor(cls) -> PowderExperiment:
        raise NotImplementedError

    @classmethod
    def get_length(cls):
        return len(cls.make_empty().list_repr)

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


import torch

class PowderTensor(Tensor):
    example_powder_experiment: PowderExperiment = PowderExperiment.make_empty()

    def new_empty(self, *sizes, dtype=None, device=None, requires_grad=False):
        dtype = dtype if dtype is not None else self.dtype
        device = device if device is not None else self.device
        return PowderTensor(torch.empty(*sizes, dtype=dtype, device=device, requires_grad=requires_grad))

    @staticmethod
    def __new__(cls, tensor) -> PowderTensor:
        return torch.Tensor.as_subclass(tensor, cls)

    #noinspection PyTypeChecker
    def get_lattice_params(self) -> PowderTensor:
        region = self.example_powder_experiment.lattice_param_region
        return self[..., region.start:region.end]

    # noinspection PyTypeChecker
    def get_atomic_site(self, index: int) -> PowderTensor:
        region = self.example_powder_experiment.atomic_site_regions[index]
        return self[..., region.start:region.end]

    # noinspection PyTypeChecker
    def get_spacegroups(self) -> PowderTensor:
        region = self.example_powder_experiment.spacegroup_region
        return self[..., region.start:region.end]

    # noinspection PyTypeChecker
    def get_artifacts(self) -> PowderTensor:
        region = self.example_powder_experiment.artifacts_region
        return self[..., region.start:region.end]

    # noinspection PyTypeChecker
    def get_domain(self) -> PowderTensor:
        region = self.example_powder_experiment.domain_region
        return self[..., region.start:region.end]

    # noinspection PyTypeChecker
    def to_sample(self) -> PowderExperiment:
        raise NotImplementedError


