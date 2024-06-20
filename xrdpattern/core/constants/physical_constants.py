import json
import os.path
from typing import Literal, Union

from pymatgen.core import Species, Element

DIRPATH = os.path.dirname(__file__)
SCATTERING_PARAMS_FILENAME = 'atomic_scattering_params.json'
COVALENT_RADI_FILENAME = 'covalent_radius.json'
VDW_FILENAME = 'vdw_radius.json'

ElementSymbol = Literal['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db']
CrystalSystem = Literal["cubic", "hexagonal", "monoclinic", "orthorhombic", "tetragonal", "triclinic", "trigonal"]

# ---------------------------------------------------------

class UnknownSite:
    symbol = 'NaN'

class Void:
    symbol = '⊥'

class PhysicalConstants:
    _vdw : dict[str, float] = {}
    _covalent : dict[str, float] = {}
    _scattering_params : dict[str, tuple] = {}
    _is_initialized : bool = False

    @classmethod
    def initialize(cls):
        cls._vdw = cls._load_vdw()
        cls._covalent = cls._load_covalent()
        cls._scattering_params = cls._load_scattering_params()
        cls._is_initialized = True

    @classmethod
    def _load_vdw(cls) -> dict[str, float]:
        return cls._load_json_file(fpath=os.path.join(DIRPATH, VDW_FILENAME))

    @classmethod
    def _load_covalent(cls) -> dict[str, float]:
        return cls._load_json_file(fpath=os.path.join(DIRPATH, COVALENT_RADI_FILENAME))

    @classmethod
    def _load_scattering_params(cls) -> dict[str, tuple]:
        return cls._load_json_file(fpath=os.path.join(DIRPATH, SCATTERING_PARAMS_FILENAME))

    @staticmethod
    def _load_json_file(fpath: str) -> dict:
        with open(fpath) as file:
            return json.load(file)

    # ---------------------------------------------------------
    # get

    @classmethod
    def get_vdw_radius(cls, element_symbol: ElementSymbol) -> float:
        return cls._vdw[element_symbol]

    @classmethod
    def get_covalent(cls, element_symbol: ElementSymbol) -> float:
        return cls._covalent[element_symbol]

    @classmethod
    def get_scattering_params(cls, species: Union[Element,Species]) -> tuple:
        if isinstance(species, Species):
            symbol = str(species.element.symbol)
        else:
            symbol = species.symbol

        return cls._scattering_params[symbol]

    @classmethod
    def print_all(cls):
        print("Van der Waals radii:", cls._vdw)
        print("Covalent radii:", cls._covalent)
        print("Scattering parameters:", cls._scattering_params)

PhysicalConstants.initialize()


if __name__ == "__main__":
    provider = PhysicalConstants()
    provider.print_all()