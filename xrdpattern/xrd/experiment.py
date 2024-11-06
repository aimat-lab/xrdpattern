from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import torch
from torch import Tensor

from xrdpattern.crystal import CrystalStructure, CrystalBase, AtomicSite, Lengths, Angles
from holytools.abstract import JsonDataclass

NUM_SPACEGROUPS = 230
MAX_ATOMIC_SITES = 100

# ---------------------------------------------------------

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

    @classmethod
    def from_structure(cls, structure : CrystalStructure, crystallite_size : float, is_simulated : bool):
        powder = PowderSample(crystal_structure=structure, crystallite_size=crystallite_size)
        artifacts = Artifacts.mk_empty()
        return cls(powder=powder, artifacts=artifacts, is_simulated=is_simulated)


    def __post_init__(self):
        if len(self.crystal_structure.base) > MAX_ATOMIC_SITES:
            raise ValueError(f"Too many atomic sites in base: {len(self.crystal_structure.base)}")

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

        if structure.spacegroup is None:
            spg_logits_list = [float('nan') for _ in range(NUM_SPACEGROUPS)]
        else:
            spg_logits_list = [1000 if j + 1 == structure.spacegroup else 0 for j in range(NUM_SPACEGROUPS)]
        self.spacegroup_region : QuantityRegion = self.add_region(list_obj=spg_logits_list)

        artifacts_list = self.artifacts.as_list()
        self.artifacts_region : QuantityRegion = self.add_region(artifacts_list)

        is_simulated = [self.is_simulated]
        self.domain_region : QuantityRegion = self.add_region(is_simulated)


    def add_region(self, list_obj : list) -> QuantityRegion:
        current_len = len(self.list_repr)
        region = QuantityRegion(obj=list_obj, start=current_len, end=current_len + len(list_obj))
        to_add = [x if not x is None else torch.nan for x in list_obj]
        self.list_repr += to_add
        return region

    @staticmethod
    def get_padded_base(base: CrystalBase, nan_padding : bool) -> CrystalBase:
        def make_padding_site():
            if nan_padding:
                site = AtomicSite.make_placeholder()
            else:
                site = AtomicSite.make_void()
            return site

        delta = MAX_ATOMIC_SITES - len(base)
        padded_base = base + [make_padding_site() for _ in range(delta)]
        return padded_base


    def to_tensor(self, dtype : torch.dtype = torch.get_default_dtype(), device : torch.device = torch.get_default_device()) -> LabelTensor:
        tensor = torch.tensor(self.list_repr, dtype=dtype, device=device)
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
        artifacts = Artifacts(primary_wavelength=None, secondary_wavelength=None)
        structure.calculate_properties()

        return cls(powder=powder, artifacts=artifacts, is_simulated=False)


    @classmethod
    def make_empty(cls, is_simulated : bool = False) -> PowderExperiment:
        lengths = Lengths(a=None, b=None, c=None)
        angles = Angles(alpha=None, beta=None, gamma=None)
        base = CrystalBase()

        structure = CrystalStructure(lengths=lengths, angles=angles, base=base)
        sample = PowderSample(crystal_structure=structure,crystallite_size=None, temp_in_celcius=None)
        artifacts = Artifacts.mk_empty()

        return cls(sample, artifacts, is_simulated=is_simulated)


@dataclass
class Artifacts(JsonDataclass):
    primary_wavelength: Optional[float]
    secondary_wavelength: Optional[float]

    @classmethod
    def mk_empty(cls):
        return cls(primary_wavelength=None, secondary_wavelength=None)

    def as_list(self) -> list[float]:
        return [self.primary_wavelength, self.secondary_wavelength]


@dataclass
class PowderSample(JsonDataclass):
    crystal_structure: CrystalStructure
    crystallite_size: Optional[float] = None
    temp_in_celcius : Optional[float] = None
    shape_factor : Optional[float] = 0.9


class LabelTensor(Tensor):
    example_experiment: PowderExperiment = PowderExperiment.make_empty()
    lattice_param_region : QuantityRegion = example_experiment.lattice_param_region
    atomic_site_regions : list[QuantityRegion] = example_experiment.atomic_site_regions
    spacegroup_region : QuantityRegion = example_experiment.spacegroup_region
    artifacts_region : QuantityRegion = example_experiment.artifacts_region
    domain_region : QuantityRegion = example_experiment.domain_region

    def new_empty(self, *sizes, dtype=None, device=None, requires_grad=False):
        dtype = dtype if dtype is not None else self.dtype
        device = device if device is not None else self.device
        return LabelTensor(torch.empty(*sizes, dtype=dtype, device=device, requires_grad=requires_grad))

    @staticmethod
    def __new__(cls, tensor) -> LabelTensor:
        return torch.Tensor.as_subclass(tensor, cls)

    #noinspection PyTypeChecker
    def get_lattice_params(self) -> LabelTensor:
        return self[..., self.lattice_param_region.start:self.lattice_param_region.end]

    # noinspection PyTypeChecker
    def get_atomic_site(self, index: int) -> LabelTensor:
        region = self.atomic_site_regions[index]
        return self[..., region.start:region.end]

    # noinspection PyTypeChecker
    def get_spg_logits(self) -> LabelTensor:
        return self[..., self.spacegroup_region.start:self.spacegroup_region.end]

    def get_spg_probabilities(self):
        logits = self.get_spg_logits()
        return torch.softmax(logits, dim=-1)

    # noinspection PyTypeChecker
    def get_artifacts(self) -> LabelTensor:
        return self[..., self.artifacts_region.start:self.artifacts_region.end]

    # noinspection PyTypeChecker
    def get_simulated_probability(self) -> LabelTensor:
        return self[..., self.domain_region.start:self.domain_region.end]

    # noinspection PyTypeChecker
    def to_sample(self) -> PowderExperiment:
        raise NotImplementedError
