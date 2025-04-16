from __future__ import annotations

import json
import math
from typing import Iterable

from xrdpattern.serialization import Serializable
from .atomic_site import AtomSite


# ---------------------------------------------------------

class CrystalBasis(Serializable):
    def __init__(self, atomic_sites : list[AtomSite]):
        super().__init__()
        self.atom_sites : list[AtomSite] = atomic_sites

    @classmethod
    def empty(cls):
        return cls(atomic_sites=[])

    def calculate_atomic_volume(self) -> float:
        total_atomic_volume = 0
        for site in self.atom_sites:
            covalent_radius = site.atom.get_covalent()
            vdw_radius = site.atom.get_vdw_radius()

            radius = (covalent_radius + vdw_radius) / 2
            atomic_volume = 4 / 3 * math.pi * radius ** 3
            total_atomic_volume += atomic_volume * site.occupancy

        return total_atomic_volume

    def get_wyckoffs(self) -> list[str]:
        wyckoff_symbols = [site.wyckoff_letter for site in self]
        if None in wyckoff_symbols:
            raise ValueError('Wyckoff symbols are not defined for all sites')

        return wyckoff_symbols

    # ---------------------------------------------------------
    # list interface

    def append(self, item : AtomSite):
        self.atom_sites.append(item)

    def __add__(self, other : list[AtomSite]):
        new_base = CrystalBasis.empty()
        for site in self:
            new_base.append(site)
        for site in other:
            new_base.append(site)
        return new_base

    def __iadd__(self, other):
        for item in other:
            self.append(item)
        return self

    def __iter__(self) -> Iterable[AtomSite]:
        return iter(self.atom_sites)

    def __len__(self):
        return len(self.atom_sites)

    def __getitem__(self, item):
        return self.atom_sites[item]

    # ---------------------------------------------------------
    # save/load

    @classmethod
    def from_str(cls, s: str):
        site_strs = json.loads(s)
        return cls([AtomSite.from_str(site_str) for site_str in site_strs])

    def to_str(self) -> str:
        return json.dumps([site.to_str() for site in self])

    def __str__(self):
        return str([x for x in self])