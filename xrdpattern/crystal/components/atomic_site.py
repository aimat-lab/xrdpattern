from __future__ import annotations

import json, os
from dataclasses import dataclass
from typing import Optional

from pymatgen.core import Species

from xrdpattern.serialization import Serializable

ScatteringParams = tuple[float, float, float, float, float, float, float, float]
#---------------------------------------------------------

@dataclass
class AtomSite(Serializable):
    """x,y,z are the coordinates of the site given in the basis of the lattice"""
    x: Optional[float]
    y: Optional[float]
    z: Optional[float]
    occupancy : Optional[float]
    species_str : str
    wyckoff_letter : Optional[str] = None

    def __post_init__(self):
        self.atom : Atom = Atom(symbol=self.species_str)

    def as_list(self) -> list[float]:
        site_arr = [*self.atom.get_scattering_params, self.x, self.y, self.z, self.occupancy]
        return site_arr

    # ---------------------------------------------------------
    # save/load

    def to_str(self) -> str:
        the_dict = {'x': self.x, 'y': self.y, 'z': self.z, 'occupancy': self.occupancy,
                    'symbol': self.species_str,
                    'wyckoff_letter': self.wyckoff_letter}

        return json.dumps(the_dict)

    @classmethod
    def from_str(cls, s: str):
        the_dict = json.loads(s)
        return cls(x=the_dict['x'], y=the_dict['y'], z=the_dict['z'], occupancy=the_dict['occupancy'],
                   species_str=the_dict['symbol'], wyckoff_letter=the_dict['wyckoff_letter'])


class Atom:
    def __init__(self, symbol : str):
        self.full_symbol : str = symbol
        self.element_symbol : str = self.as_pymatgen.element.symbol

    @property
    def as_pymatgen(self) -> Optional[Species]:
        return Species.from_str(species_string=self.full_symbol)

    # TODO: These are currently the scattering factors in pymat gen atomic_scattering_parmas.json
    # These are *different* paramters from what you may commonly see e.g. here (https://lampz.tugraz.at/~hadley/ss1/crystaldiffraction/atomicformfactors/formfactors.php)
    # since pymatgen uses a different formula to compute the form factor
    @property
    def get_scattering_params(self) -> ScatteringParams:
        # TODO: This casting only currently exists beacuse the scattering param table only has values for (unoxidized) elements, not ions
        # TODO: Normally would simply be species_symbol=str(self.species_like)
        species_symbol = self.as_pymatgen.element.symbol
        values = scattering_params[species_symbol]

        (a1, b1), (a2, b2), (a3, b3), (a4, b4) = values
        return a1, b1, a2, b2, a3, b3, a4, b4

    def get_vdw_radius(self) -> float:
        return vdw_radii[self.element_symbol]

    def get_covalent(self) -> float:
        return covalent_radii[self.element_symbol]


def load_constants_json(fname: str) -> dict:
    script_dirpath = os.path.dirname(__file__)
    crystal_dirpath = os.path.dirname(script_dirpath)
    constants_dirpath = os.path.join(crystal_dirpath, 'atomic_constants')
    fpath = os.path.join(constants_dirpath, fname)
    with open(fpath) as file:
        return json.load(file, parse_float=float, parse_int=float)


SCATTERING_PARAMS_FILENAME = 'atomic_scattering_params.json'
COVALENT_RADI_FILENAME = 'covalent_radius.json'
VDW_FILENAME = 'vdw_radius.json'

vdw_radii : dict[str, float] = load_constants_json(fname=VDW_FILENAME)
covalent_radii : dict[str, float] = load_constants_json(fname=COVALENT_RADI_FILENAME)
scattering_params : dict[str, tuple] = load_constants_json(fname=SCATTERING_PARAMS_FILENAME)


