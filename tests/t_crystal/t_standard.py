from holytools.devtools import Unittest

from CrystalStructure.crystal import CrystalStructure, AtomicSite, Lengths, Angles, CrystalBase
from CrystalStructure.crystal.atomic_site import AtomType


# ---------------------------------------------------------

class TestCrystalStandardization(Unittest):
    def setUp(self):
        primitives = Lengths(5, 3, 4)
        mock_angles = Angles(90, 90, 90)
        mock_base = CrystalBase([
            AtomicSite(x=0.5, y=0.5, z=0.5, occupancy=1.0, species_str="Si0+"),
            AtomicSite(x=0.1, y=0.1, z=0.1, occupancy=1.0, species_str="O0+"),
            AtomicSite(x=0.9, y=0.9, z=0.9, occupancy=1.0, species_str=AtomType.void_symbol)
        ])
        crystal = CrystalStructure(lengths=primitives, angles=mock_angles, base=mock_base)
        crystal.calculate_properties()
        crystal.standardize()

        self.mock_crystal = crystal


    def test_scaling(self):
        target_density = 0.5
        self.mock_crystal.scale(target_density=target_density)
        print(f'Packing density, target density = {self.mock_crystal.packing_density}, {target_density}')
        print(f'Volume scaling = {self.mock_crystal.packing_density / target_density}')
        print(f'New primitives = {self.mock_crystal.lengths.as_tuple()}')
        print(f'New packing density = {self.mock_crystal.packing_density}')
        self.assertEqual(round(self.mock_crystal.packing_density, 2), round(target_density, 2))


    def test_standardization(self):
        self.mock_crystal.standardize()
        expected_species_str_list = ['O0+', 'Si0+', AtomType.void_symbol]
        actual_specie_str_list = [site.species_str for site in self.mock_crystal.base]
        self.assertEqual(actual_specie_str_list, expected_species_str_list)

        actual_primitives = self.mock_crystal.lengths.as_tuple()
        expected_primitives = (3, 4, 5)
        self.assertEqual(actual_primitives, expected_primitives)



if __name__ == "__main__":
    TestCrystalStandardization.execute_all()