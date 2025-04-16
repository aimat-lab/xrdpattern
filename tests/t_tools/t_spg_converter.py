from holytools.devtools import Unittest

from xrdpattern.crystal.spgs import SpacegroupConverter


class SpacegroupConversionTest(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.spg_integers = range(1, 231)
        print(f'- Obtaining spg formulas')
        cls.spg_formulas = SpacegroupConverter.get_all_formulas()
        print(f'- Setup complete\n')

    def test_to_int(self):
        for spg in self.spg_formulas:
            spg_int = SpacegroupConverter.to_int(spg)
            self.assertIsInstance(spg_int, int)

    def test_to_formula(self):
        for spg in self.spg_integers:
            formula = SpacegroupConverter.to_formula(spg)
            self.assertIsInstance(formula, str)

    def test_roundtrip(self):
        for spg in self.spg_integers:
            formula = SpacegroupConverter.to_formula(spg)
            spg2 = SpacegroupConverter.to_int(formula)
            self.assertEqual(spg, spg2)


if __name__ == "__main__":
    SpacegroupConversionTest.execute_all()