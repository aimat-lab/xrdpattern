from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from typing import Optional, Literal

from distlib.util import cached_property
from pymatgen.core import Structure, Lattice, Species, Element
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from xrdpattern.serialization import JsonDataclass
from .atomic_site import AtomSite
from .base import CrystalBasis

logger = logging.getLogger(__name__)
CrystalSystem = Literal["cubic", "hexagonal", "monoclinic", "orthorhombic", "tetragonal", "triclinic", "trigonal"]
# ---------------------------------------------------------

@dataclass
class CrystalStructure(JsonDataclass):
    lattice : Lattice
    basis : CrystalBasis
    spacegroup : Optional[int] = None
    chemical_composition : Optional[str] = None
    wyckoff_symbols : Optional[list[str]] = None
    phase_fraction: Optional[float] = None

    def __post_init__(self):
        if not self.phase_fraction is None:
            if not 0 <= self.phase_fraction <= 1:
                raise ValueError(f'Phase fraction must be between 0 and 1. Got {self.phase_fraction}')

    @classmethod
    def from_cif(cls, cif_content : str) -> CrystalStructure:
        pymatgen_structure = Structure.from_str(cif_content, fmt='cif')
        crystal_structure = cls.from_pymatgen(pymatgen_structure)
        return crystal_structure

    @classmethod
    def from_pymatgen(cls, pymatgen_structure: Structure) -> CrystalStructure:
        lattice = pymatgen_structure.lattice
        base : CrystalBasis = CrystalBasis.empty()

        for index, site in enumerate(pymatgen_structure.sites):
            site_composition = site.species
            for species, occupancy in site_composition.items():
                if isinstance(species, Element):
                    species = Species(symbol=species.symbol, oxidation_state=0)
                x,y,z = lattice.get_fractional_coords(site.coords)
                atomic_site = AtomSite(x, y, z, occupancy=occupancy, species_str=str(species))
                base.append(atomic_site)

        crystal_str = cls(lattice=lattice, basis=base)

        return crystal_str

    # ---------------------------------------------------------
    # conversion

    def to_cif(self) -> str:
        pymatgen_structure = self.to_pymatgen()
        return pymatgen_structure.to(filename='', fmt='cif')

    def to_pymatgen(self) -> Structure:
        non_void_sites = self.basis.atom_sites
        atoms = [site.atom.as_pymatgen for site in non_void_sites]
        positions = [(site.x, site.y, site.z) for site in non_void_sites]

        if len(atoms) == 0:
            logger.warning('Structure has no atoms!')
            raise ValueError('Structure has no atoms! Cannot convert phase without atoms to pymatgen structure')

        return Structure(self.lattice, atoms, positions)

    def get_view(self) -> str:
        the_dict = asdict(self)
        the_dict = {str(key) : str(value) for key, value in the_dict.items() if not isinstance(value, Structure)}
        the_dict['base'] = f'{self.basis[0]}, ...'
        return json.dumps(the_dict, indent='-')

    # ---------------------------------------------------------
    # properties

    def calculate_properties(self):
        if len(self.basis) == 0:
            raise ValueError('Base is empty! Cannot calculate properties of empty crystal. Aborting ...')

        pymatgen_structure = self.to_pymatgen()
        analyzer = SpacegroupAnalyzer(structure=pymatgen_structure, symprec=0.1, angle_tolerance=10)
        symmetry_dataset = analyzer.get_symmetry_dataset()

        self.spacegroup = analyzer.get_space_group_number()
        self.wyckoff_symbols = symmetry_dataset['wyckoffs']
        self.chemical_composition = pymatgen_structure.composition.formula

    def get_standardized(self) -> CrystalStructure:
        struct = self.to_pymatgen() if len(self.basis) > 0 else Structure(self.lattice, ["H"], [[0, 0, 0]])
        analzyer = SpacegroupAnalyzer(structure=struct)
        std_struct = analzyer.get_conventional_standard_structure()
        if len(self.basis) == 0:
            return CrystalStructure(lattice=std_struct.lattice, basis=CrystalBasis.empty())
        else:
            return CrystalStructure.from_pymatgen(pymatgen_structure=std_struct)

    def scale(self, target_density: float):
        volume_scaling = self.packing_density / target_density
        self.lattice.scale(new_volume=volume_scaling*self.volume_uc)

    @cached_property
    def packing_density(self) -> float:
        volume_uc = self.volume_uc
        atomic_volume = self.basis.calculate_atomic_volume()
        return atomic_volume/volume_uc

    @cached_property
    def num_atoms(self) -> int:
        return len(self.basis)

    @cached_property
    def volume_uc(self) -> float:
        return self.lattice.volume

    @cached_property
    def crystal_system(self):
        if self.spacegroup is None:
            raise ValueError('Spacegroup is not defined. Cannot determine crystal system.')
        return self._spg_to_crystal_system(self.spacegroup)

    @staticmethod
    def _spg_to_crystal_system(spg: int) -> CrystalSystem:
        if spg <= 2:
            return "triclinic"
        if spg <= 15:
            return "monoclinic"
        if spg <= 74:
            return "orthorhombic"
        if spg <= 142:
            return "tetragonal"
        if spg <= 167:
            return "trigonal"
        if spg <= 194:
            return "hexagonal"
        return "cubic"

    @property
    def angles(self) -> tuple[float, float, float]:
        return self.lattice.angles

    @property
    def lengths(self) -> tuple[float, float, float]:
        return self.lattice.lengths

    @staticmethod
    def make_basic(basic_cls, s: str):
        if basic_cls == Lattice:
            print(f's = {s}')
            arr = s[1:-1].split(',')
            params = [float(x) for x in arr]
            return Lattice.from_parameters(*params)
        else:
            return JsonDataclass.make_basic(basic_cls, s)

    @staticmethod
    def get_basic_entry(obj):
        if isinstance(obj, Lattice):
            params = *obj.lengths, *obj.angles
            return str(params)
        else:
            return JsonDataclass.get_basic_entry(obj)