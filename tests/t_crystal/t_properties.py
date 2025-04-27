from pymatgen.core import Lattice

import tests.t_crystal.base_crystal as BaseTest
from xrdpattern.crystal import CrystalStructure, CrystalExamples


# ---------------------------------------------------------

class TestCifParsing(BaseTest.CrystalTest):
    def test_lattice_parameters(self):
        expected_lengths = [(5.801, 11.272, 5.57), (4.0809,4.0809,4.0809)]
        for crystal, (a_exp, b_exp, c_exp) in zip(self.custom_structures, expected_lengths):
            a, b, c = crystal.lattice.lengths
            self.assertAlmostEqual(a, a_exp, places=3)
            self.assertAlmostEqual(b, b_exp, places=4)
            self.assertAlmostEqual(c, c_exp, places=3)

    def test_angles(self):
        expected_angles = [(90, 90, 90), (89.676, 89.676, 89.676)]
        for crystal, (alpha_exp, beta_exp, gamma_exp) in zip(self.custom_structures, expected_angles):
            alpha, beta, gamma = crystal.lattice.angles
            self.assertEqual(alpha, alpha_exp)
            self.assertAlmostEqual(beta, beta_exp, places=3)
            self.assertEqual(gamma, gamma_exp)

    def test_num_atoms(self):
        expected_atom_counts = [4*4, 6]
        for crystal, num_atoms_exp in zip(self.custom_structures, expected_atom_counts):
            self.assertEqual(len(crystal.basis), num_atoms_exp)


    def test_to_cif(self):
        for struct, crystal in zip(self.pymatgen_structures, self.custom_structures):
            cif = crystal.to_cif()
            print(f'CIF = \n{cif}')

    def test_standardize(self):
        a,b,c = 5.801, 11.272, 5.57
        alpha, beta, gamma = 90,90,90
        
        lattice = Lattice.from_parameters(a=a, b=b, c=c, alpha=alpha, beta=beta, gamma=gamma)
        empty_phase = CrystalStructure(lattice=lattice, basis=None)
        empty_standardized = empty_phase.get_standardized()
        self.assertTrue(empty_standardized.basis is None)



        nonempty_phase = CrystalStructure.from_cif(cif_content=CrystalExamples.get_cif_content())
        nonempty_standardized = nonempty_phase.get_standardized()
        for j,l in enumerate(sorted([a,b,c])):
            self.assertAlmostEqual(nonempty_standardized.lengths[j],l)

        for k,angle in enumerate(sorted([alpha, beta, gamma])):
            self.assertAlmostEqual(nonempty_standardized.angles[k], angle)

        self.assertTrue(len(nonempty_standardized.basis) == len(nonempty_phase.basis))


if __name__ == "__main__":
    TestCifParsing.execute_all()