from xrdpattern.powder import Lengths, AtomicSite, CrystalBase, Angles, Void
from pymatgen.core import Species
from pymatgen.core.structure import Structure

from holytools.devtools import Unittest
from holytools.file import PlaintextFile
from xrdpattern.powder import CrystalStructure
from tests.t_powder.examples import Examples

# ---------------------------------------------------------

class TestCifParsing(Unittest):
    @classmethod
    def setUpClass(cls):
        cif_fpath = Examples.get_cif_fpath(secondary=True)
        print(f'Cif content from example: {PlaintextFile.get_text(cif_fpath)}')
        cls.pymatgen_structure = Structure.from_file(filename=cif_fpath)
        crystal = CrystalStructure.from_cif(fpath=cif_fpath)
        crystal.calculate_properties()
        cls.crystal = crystal


    def test_lattice_parameters(self):
        # Unpack primitives into a, b, c
        a, b, c = self.crystal.lengths
        self.assertAlmostEqual(a, 5.801, places=3)
        self.assertAlmostEqual(b, 11.272, places=3)
        self.assertAlmostEqual(c, 5.57, places=3)

    def test_angles(self):
        # Unpack angles into alpha, beta, gamma
        alpha, beta, gamma = self.crystal.angles
        self.assertEqual(alpha, 90)
        self.assertEqual(beta, 90)
        self.assertEqual(gamma, 90)

    def test_volume_uc(self):
        self.assertAlmostEqual(self.crystal.volume_uc, 364.21601704000005, places=5)

    def test_num_atoms(self):
        self.assertEqual(self.crystal.num_atoms, 16)

    def test_wyckoff_symbols(self):
        expected_symbols = ['d', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'c', 'c', 'c', 'c', 'd', 'd', 'd', 'd']
        self.assertEqual(self.crystal.wyckoff_symbols, expected_symbols)

    def test_crystal_system(self):
        self.assertEqual(self.crystal.crystal_system, 'orthorhombic')

    def test_spacegroup(self):
        self.assertEqual(self.crystal.space_group, 57)


class TestPymatgenCompatibility(Unittest):
    @classmethod
    def setUpClass(cls):
        pymatgen_structure = Structure.from_file(Examples.get_cif_fpath(secondary=True))
        cls.crystal = CrystalStructure.from_pymatgen(pymatgen_structure=pymatgen_structure)
        cls.pymatgen_structure = pymatgen_structure

    def test_pymatgen_roundtrip(self):
        self.assertEqual(self.crystal.to_pymatgen(), self.pymatgen_structure)


class TestCrystalCalculations(Unittest):
    def setUp(self):
        self.primitives = Lengths(5, 3, 4)
        self.angles = Angles(90, 90, 90)
        self.base = CrystalBase([
            AtomicSite(x=0.5, y=0.5, z=0.5, occupancy=1.0, species=Species("Si")),
            AtomicSite(x=0.1, y=0.1, z=0.1, occupancy=1.0, species=Species("O")),
            AtomicSite(x=0.9, y=0.9, z=0.9, occupancy=1.0, species=Void())
        ])
        crystal = CrystalStructure(lengths=self.primitives, angles=self.angles, base=self.base)
        crystal.calculate_properties()
        crystal.standardize()
        self.crystal = crystal

    def test_standardization(self):
        self.crystal.standardize()
        expected_species_list = ['O', 'Si', Void.get_symbol()]
        acrual_species_list = [self.get_site_symbol(site) for site in self.crystal.base]
        self.assertEqual(acrual_species_list, expected_species_list)

        actual_primitives = self.crystal.lengths.as_tuple()
        expected_primitives = (3,4,5)
        self.assertEqual(actual_primitives, expected_primitives)


    def test_atomic_volume(self):
        print(f'self.crystal atomic volume fraction = {self.crystal.packing_density}')

    def test_scaling(self):
        target_density = 0.5
        self.crystal.scale(target_density=target_density)
        print(f'Packing density, target density = {self.crystal.packing_density}, {target_density}')
        print(f'Volume scaling = {self.crystal.packing_density/target_density}')
        print(f'New primitives = {self.crystal.lengths.as_tuple()}')
        print(f'New packing density = {self.crystal.packing_density}')
        self.assertEqual(round(self.crystal.packing_density,2), round(target_density,2))

    @staticmethod
    def get_site_symbol(site : AtomicSite):
        if isinstance(site.species, Void):
            symbol = Void.get_symbol()
        else:
            symbol = site.species.element.symbol
        return symbol

if __name__ == '__main__':
    # TestCifParsing.execute_all()
    # TestPymatgenCompatibility.execute_all()
    TestCrystalCalculations.execute_all()
