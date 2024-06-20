from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Union, Optional

import torch
from pymatgen.core import Species, Element

from holytools.abstract import Serializable
from xrdpattern.core import Void, UnknownSite, PhysicalConstants

ScatteringParams = tuple[float, float, float, float, float, float, float, float]
#---------------------------------------------------------

@dataclass
class AtomicSite(Serializable):
    """x,y,z are the coordinates of the site given in the basis of the lattice"""
    x: float
    y: float
    z: float
    occupancy : float
    species : Union[Element,Species, Void, UnknownSite]
    wyckoff_letter : Optional[str] = None

    def __post_init__(self):
        if self.is_nonstandard():
           return

        if not 0 <= self.occupancy <= 1:
            raise ValueError('Occupancy must be between 0 and 1')

    @classmethod
    def make_void(cls) -> AtomicSite:
        return cls(x=torch.nan, y=torch.nan, z=torch.nan, occupancy=0, species=Void())

    @classmethod
    def make_placeholder(cls):
        return cls(x=torch.nan, y=torch.nan, z=torch.nan, occupancy=torch.nan, species=UnknownSite())

    def is_nonstandard(self) -> bool:
        if not isinstance(self.species, Species):
            return True
        return False

    # ---------------------------------------------------------
    # properties

    def as_list(self) -> list[float]:
        site_arr = [*self.get_scattering_params(), self.x, self.y, self.z, self.occupancy]
        return site_arr

    # TODO: These are currently the scattering factors in pymat gen atomic_scattering_parmas.json
    # These are *different* paramters from what you may commonly see e.g. here (https://lampz.tugraz.at/~hadley/ss1/crystaldiffraction/atomicformfactors/formfactors.php)
    # since pymatgen uses a different formula to compute the form factor
    def get_scattering_params(self) -> ScatteringParams:
        if isinstance(self.species, Species) or isinstance(self.species, Element):
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

    # ---------------------------------------------------------
    # save/load

    def to_str(self) -> str:
        the_dict = {'x': self.x, 'y': self.y, 'z': self.z, 'occupancy': self.occupancy,
                    'species': str(self.species),
                    'wyckoff_letter': self.wyckoff_letter}

        return json.dumps(the_dict)

    @classmethod
    def from_str(cls, s: str):
        the_dict = json.loads(s)
        species_symbol = the_dict['species']
        if species_symbol == Void.symbol:
            species = Void()
        elif species_symbol == UnknownSite.symbol:
            species = UnknownSite()
        else:
            species = Species.from_str(species_symbol)

        return cls(x=the_dict['x'], y=the_dict['y'], z=the_dict['z'],
                   occupancy=the_dict['occupancy'],
                   species=species,
                   wyckoff_letter=the_dict['wyckoff_letter'])
