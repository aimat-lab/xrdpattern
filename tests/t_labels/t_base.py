from holytools.devtools import Unittest
from pymatgen.core import Species

from xrdpattern.examples import LabelExamples


class TestCrystalBase(Unittest):
    def test_scattering_params(self):
        base = LabelExamples.get_base()
        seen_species = set()

        for atomic_site in base:
            params = atomic_site.get_scattering_params()
            self.assertEqual(len(params), 8)
            for p in params:
                self.assertIsInstance(p, float)
            if not atomic_site.species in seen_species:
                print(f'Scattering params for species \"{atomic_site.species}\" a1, a2, a3, a4, b1, b2, b3, b4 = {params}')
            seen_species.add(atomic_site.species)


    def test_site_dictionaries(self):
        base = LabelExamples.get_base(mute=False)
        site_dictionaries = base.as_site_dictionaries()

        coordinates = list(site_dictionaries.keys())
        max_err = 10**(-2)
        target_coordinate = (0,0,0.0154)

        def dist(coor1, coord2):
            return sum([(x-y)**2 for x,y in zip(coor1, coord2)])**(1/2)

        match = None
        for coord in coordinates:
            match_found = any([dist(coord, target_coordinate) < max_err])
            if match_found:
                match = coord

        self.assertIsNotNone(match)
        self.assertIn(Species(f'Fe3+'), site_dictionaries[match])

    # def test_shift_coordinates(self):
    #     test_cases = [-1.7, -0.5, 0.5, 1.0, 2.1, 5.5, -2.1, -3.3]
    #     expected_results = [0.3, 0.5, 0.5, 0.0, 0.1, 0.5, 0.9, 0.7]
    #     for test_input, expected in zip(test_cases, expected_results):
    #         result = AtomicSite.shift_into_unit(test_input)
    #         self.assertAlmostEqual(result, expected, places=5)

if __name__ == '__main__':
    TestCrystalBase.execute_all()