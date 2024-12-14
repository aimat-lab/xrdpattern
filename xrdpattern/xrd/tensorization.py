from __future__ import annotations
import torch
from tensordict import TensorDict
from torch import Tensor


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

