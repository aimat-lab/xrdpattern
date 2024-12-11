from databases.tools.spg_converter import SpacegroupConverter
from holytools.devtools import Unittest



class SpacegroupConversionTest(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.spg_integers = range(1, 231)
        cls.spg_formulas =

    #tests all formula to inv + int instance test
    def test_to_int(self):

    #tests all ints to formula + str instance test

    def test_roundtrip(self):
        for spg in self.spg_integers:
            formula = SpacegroupConverter.to_formula(spg)
            spg2 = SpacegroupConverter.to_int(formula)
            print(f'Converted {spg} to {formula} and back to {spg2}')
            self.assertEqual(spg, spg2)


if __name__ == "__main__":
    SpacegroupConversionTest.execute_all()