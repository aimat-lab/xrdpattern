from __future__ import annotations

import torch
from torch import Tensor

from xrdpattern.powder import PatternLabel


class PowderTensor(Tensor):
    example_powder_experiment: PatternLabel = PatternLabel.make_empty()

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
    def to_sample(self) -> PatternLabel:
        raise NotImplementedError
