import tests.t_crystal.crystal_test as BaseTest

# ---------------------------------------------------------

class TestCifParsing(BaseTest.CrystalTest):
    def test_lattice_parameters(self):
        expected_lengths = [(5.801, 11.272, 5.57), (4.0809,4.0809,4.0809)]
        for crystal, (a_exp, b_exp, c_exp) in zip(self.custom_structures, expected_lengths):
            a, b, c = crystal.lengths
            self.assertAlmostEqual(a, a_exp, places=3)
            self.assertAlmostEqual(b, b_exp, places=4)
            self.assertAlmostEqual(c, c_exp, places=3)

    def test_angles(self):
        expected_angles = [(90, 90, 90), (89.676, 89.676, 89.676)]
        for crystal, (alpha_exp, beta_exp, gamma_exp) in zip(self.custom_structures, expected_angles):
            alpha, beta, gamma = crystal.angles
            self.assertEqual(alpha, alpha_exp)
            self.assertAlmostEqual(beta, beta_exp, places=3)
            self.assertEqual(gamma, gamma_exp)


    def test_num_atoms(self):
        expected_atom_counts = [4*4, 6]
        for crystal, num_atoms_exp in zip(self.custom_structures, expected_atom_counts):
            self.assertEqual(len(crystal.base), num_atoms_exp)


    def test_to_cif(self):
        for struct, crystal in zip(self.pymatgen_structures, self.custom_structures):
            cif = crystal.to_cif()
            print(f'CIF = \n{cif}')


if __name__ == "__main__":
    TestCifParsing.execute_all()