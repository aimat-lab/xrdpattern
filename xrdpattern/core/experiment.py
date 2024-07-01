from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import torch
from torch import Tensor

from CrystalStructure.crystal import CrystalStructure, CrystalBase, AtomicSite, Lengths, Angles
from holytools.abstract import JsonDataclass

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
class PowderExperiment(JsonDataclass):
    powder : PowderSample
    artifacts : Artifacts
    is_simulated : bool

    def __post_init__(self):
        self.list_repr = []
        structure = self.crystal_structure

        a, b, c = structure.lengths
        alpha, beta, gamma = structure.angles
        lattice_params = [a, b, c, alpha, beta, gamma]
        self.lattice_param_region : QuantityRegion = self.add_region(list_obj=lattice_params)

        self.atomic_site_regions : list[QuantityRegion] = []
        base = structure.base
        padded_base = self.get_padded_base(base=base, nan_padding=base.is_empty())
        for atomic_site in padded_base:
            region_obj = self.add_region(list_obj=atomic_site.as_list())
            self.atomic_site_regions.append(region_obj)

        if structure.space_group is None:
            spacegroup_list = [float('nan') for _ in range(NUM_SPACEGROUPS)]
        else:
            spacegroup_list = [j + 1 == structure.space_group for j in range(NUM_SPACEGROUPS)]
        self.spacegroup_region : QuantityRegion = self.add_region(list_obj=spacegroup_list)

        artifacts_list = self.artifacts.as_list()
        self.artifacts_region : QuantityRegion = self.add_region(artifacts_list)

        domain_list = [self.is_simulated]
        self.domain_region : QuantityRegion = self.add_region(domain_list)


    def add_region(self, list_obj : list) -> QuantityRegion:
        current_len = len(self.list_repr)
        region = QuantityRegion(obj=list_obj, start=current_len, end=current_len + len(list_obj))
        to_add = [x if not x is None else torch.nan for x in list_obj]
        self.list_repr += to_add
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


    def to_tensor(self) -> LabelTensor:
        tensor = torch.tensor(self.list_repr)
        return LabelTensor(tensor)

    # ---------------------------------------------------------
    # properties

    def is_partial_label(self) -> bool:
        powder_tensor = torch.tensor(self.list_repr)
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

    @classmethod
    def get_length(cls):
        empty = cls.make_empty()
        return len(empty.list_repr)

    # ---------------------------------------------------------
    # save/load

    @classmethod
    def from_cif(cls, cif_content : str) -> PowderExperiment:
        structure = CrystalStructure.from_cif(cif_content)
        powder = PowderSample(crystal_structure=structure)
        artifacts = Artifacts(primary_wavelength=None,
                              secondary_wavelength=None,
                              secondary_to_primary=None)

        return cls(powder=powder, artifacts=artifacts, is_simulated=False)


    @classmethod
    def make_empty(cls) -> PowderExperiment:
        lengths = Lengths(a=None, b=None, c=None)
        angles = Angles(alpha=None, beta=None, gamma=None)
        base = CrystalBase()

        structure = CrystalStructure(lengths=lengths, angles=angles, base=base)
        sample = PowderSample(crystallite_size=None, crystal_structure=structure, temp_in_celcius=None)
        artifacts = Artifacts(primary_wavelength=None,
                              secondary_wavelength=None,
                              secondary_to_primary=None,
                              shape_factor=None)

        return cls(sample, artifacts, is_simulated=False)


@dataclass
class Artifacts(JsonDataclass):
    primary_wavelength: Optional[float]
    secondary_wavelength: Optional[float]
    secondary_to_primary: Optional[float]
    shape_factor : Optional[float] = 0.9

    def as_list(self) -> list[float]:
        return [self.primary_wavelength, self.secondary_wavelength, self.secondary_to_primary, self.shape_factor]


@dataclass
class PowderSample(JsonDataclass):
    crystal_structure: CrystalStructure
    crystallite_size: Optional[float] = None
    temp_in_celcius : Optional[float] = None


class LabelTensor(Tensor):
    example_powder_experiment: PowderExperiment = PowderExperiment.make_empty()

    def new_empty(self, *sizes, dtype=None, device=None, requires_grad=False):
        dtype = dtype if dtype is not None else self.dtype
        device = device if device is not None else self.device
        return LabelTensor(torch.empty(*sizes, dtype=dtype, device=device, requires_grad=requires_grad))

    @staticmethod
    def __new__(cls, tensor) -> LabelTensor:
        return torch.Tensor.as_subclass(tensor, cls)

    #noinspection PyTypeChecker
    def get_lattice_params(self) -> LabelTensor:
        region = self.example_powder_experiment.lattice_param_region
        return self[..., region.start:region.end]

    # noinspection PyTypeChecker
    def get_atomic_site(self, index: int) -> LabelTensor:
        region = self.example_powder_experiment.atomic_site_regions[index]
        return self[..., region.start:region.end]

    # noinspection PyTypeChecker
    def get_spacegroups(self) -> LabelTensor:
        region = self.example_powder_experiment.spacegroup_region
        return self[..., region.start:region.end]

    # noinspection PyTypeChecker
    def get_artifacts(self) -> LabelTensor:
        region = self.example_powder_experiment.artifacts_region
        return self[..., region.start:region.end]

    # domain = 1 : simulated
    # domain = 0 : experimental
    # noinspection PyTypeChecker
    def get_domain(self) -> LabelTensor:
        region = self.example_powder_experiment.domain_region
        return torch.sigmoid(self[..., region.start:region.end])

    # noinspection PyTypeChecker
    def to_sample(self) -> PowderExperiment:
        raise NotImplementedError
