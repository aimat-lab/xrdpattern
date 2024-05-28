from __future__ import annotations

from dataclasses import dataclass
from typing import Union, Optional

import torch
from pymatgen.core import Species
from xrdpattern.core.constants import PhysicalConstants, Void, UnknownSite
from xrdpattern.core.constants import ElementSymbol
import math
# ---------------------------------------------------------

ScatteringParams = tuple[float, float, float, float, float, float, float, float]

@dataclass
class AtomicSite:
    """x,y,z are the coordinates of the site given in the basis of the lattice"""
    x: float
    y: float
    z: float
    occupancy : float
    species : Union[Species, Void, UnknownSite]
    wyckoff_letter : Optional[str] = None

    def __post_init__(self):
        if self.is_nonstandard():
           return

        if not 0 <= self.occupancy <= 1:
            raise ValueError('Occupancy must be between 0 and 1')

        for val in [self.x, self.y,self.z]:
            if not self.in_unit_interval(val):
                print(f'Warning: Fractional coordinate {val} is not in unit interval')

    @staticmethod
    def in_unit_interval(val : float) -> bool:
        epsilon = 1e-6
        in_unit_interval = True
        if not (0 - epsilon < val < 1 +epsilon):
            in_unit_interval = False
        return in_unit_interval

    @staticmethod
    def shift_into_unit(x : float):
        if x >= 0:
            n = int(x)
        else:
            n = int(x-1)
        return x - n

    @classmethod
    def make_void(cls) -> AtomicSite:
        return cls(x=torch.nan, y=torch.nan, z=torch.nan, occupancy=0, species=Void())

    @classmethod
    def make_placeholder(cls):
        return cls(x=torch.nan, y=torch.nan, z=torch.nan, occupancy=torch.nan, species=UnknownSite())

    def is_nonstandard(self) -> bool:
        if isinstance(self.species, Void):
            return True
        if isinstance(self.species, UnknownSite):
            return True
        return False

    # ---------------------------------------------------------
    # get properties

    def as_list(self) -> list[float]:
        a1,a2,a3,a4,b1,b2,b3,b4 = self.get_scattering_params()
        x, y, z, occupancy = self.x, self.y, self.z, self.occupancy
        site_arr = [a1, a2, a3, a4, b1, b2, b3, b4, x, y, z, occupancy]
        return site_arr

    # TODO: These are currently the scattering factors in pymat gen atomic_scattering_parmas.json
    # These are *different* paramters from what you may commonly see e.g. here (https://lampz.tugraz.at/~hadley/ss1/crystaldiffraction/atomicformfactors/formfactors.php)
    # since pymatgen uses a different formula to compute the form factor
    def get_scattering_params(self) -> ScatteringParams:
        if isinstance(self.species, Species):
            values = PhysicalConstants.get_scattering_params(species=self.species)
        elif isinstance(self.species, Void):
            values = (0, 0), (0, 0), (0, 0), (0, 0)
        elif isinstance(self.species, UnknownSite):
            fnan = float('nan')
            values = (fnan,fnan), (fnan,fnan), (fnan,fnan), (fnan,fnan)
        else:
            raise ValueError(f'Unknown species type: {self.species}')

        (a1, b1), (a2, b2), (a3, b3), (a4, b4) = values
        return a1, b1, a2, b2, a3, b3, a4, b4


class CrystalBase(list[AtomicSite]):
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


    def get_wyckoffs(self) -> list[str]:
        wyckoff_symbols = [site.wyckoff_letter for site in self]
        if None in wyckoff_symbols:
            raise ValueError('Wyckoff symbols are not defined for all sites')

        return wyckoff_symbols