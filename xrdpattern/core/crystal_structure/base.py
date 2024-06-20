from __future__ import annotations

import json
from typing import Optional

from holytools.abstract import Serializable
from xrdpattern.core.constants import PhysicalConstants, ElementSymbol
from .atomic_site import AtomicSite
import math

# ---------------------------------------------------------

class CrystalBase(Serializable):
    def __init__(self, atomic_sites : Optional[list[AtomicSite]] = None):
        super().__init__()
        if not atomic_sites is None:
            self.atomic_sites : list[AtomicSite] = atomic_sites
        else:
            self.atomic_sites : list[AtomicSite] = []

    def calculate_atomic_volume(self) -> float:
        total_atomic_volume = 0
        for site in self.get_non_void_sites():
            element_symbol : ElementSymbol = site.species.element.symbol
            covalent_radius  = PhysicalConstants.get_covalent(element_symbol=element_symbol)
            vdw_radius = PhysicalConstants.get_vdw_radius(element_symbol=element_symbol)

            radius = (covalent_radius + vdw_radius) / 2
            atomic_volume = 4 / 3 * math.pi * radius ** 3
            total_atomic_volume += atomic_volume * site.occupancy

        return total_atomic_volume

    def get_non_void_sites(self) -> list[AtomicSite]:
        return [site for site in self if not site.is_nonstandard()]

    def as_site_dictionaries(self) -> dict:
        coordinate_map = {}
        for atom_site in self:
            coords = (atom_site.x, atom_site.y, atom_site.z)
            if not coords in coordinate_map:
                coordinate_map[coords] = {}
            coordinate_map[coords][atom_site.species] = atom_site.occupancy

        print(f'Coordinate map = {coordinate_map}')
        return coordinate_map

    def is_empty(self) -> bool:
        return len(self) == 0

    def get_wyckoffs(self) -> list[str]:
        wyckoff_symbols = [site.wyckoff_letter for site in self]
        if None in wyckoff_symbols:
            raise ValueError('Wyckoff symbols are not defined for all sites')

        return wyckoff_symbols

    # ---------------------------------------------------------
    # list interface

    def append(self, item : AtomicSite):
        self.atomic_sites.append(item)

    def __add__(self, other : list[AtomicSite]):
        new_base = CrystalBase()
        for site in self:
            new_base.append(site)
        for site in other:
            new_base.append(site)
        return new_base

    def __iadd__(self, other):
        for item in other:
            self.append(item)
        return self

    def __iter__(self):
        return iter(self.atomic_sites)

    def __len__(self):
        return len(self.atomic_sites)

    def __getitem__(self, item):
        return self.atomic_sites[item]

    # ---------------------------------------------------------
    # save/load

    @classmethod
    def from_str(cls, s: str):
        site_strs = json.loads(s)
        return cls([AtomicSite.from_str(site_str) for site_str in site_strs])

    def to_str(self) -> str:
        return json.dumps([site.to_str() for site in self])
