from holytools.devtools import Unittest

from xrdpattern.crystal import CrystalBasis, AtomSite, CrystalExamples


# ---------------------------------------------------------

class TestCrystalBase(Unittest):
    def test_scattering_params(self):
        mock_base = CrystalBasis([
            AtomSite(x=0.5, y=0.5, z=0.5, occupancy=1.0, species_str="Si0"),
        ])
        real_base = CrystalExamples.get_base()

        for base in [mock_base, real_base]:
            seen_species = set()

            for atomic_site in base:
                params = atomic_site.atom.get_scattering_params
                self.assertEqual(len(params), 8)
                for p in params:
                    self.assertIsInstance(p, float)
                if not atomic_site.atom in seen_species:
                    print(f'Scattering params for species \"{atomic_site.species_str}:\n a1, a2, a3, a4, b1, b2, b3, b4 = {params}')
                seen_species.add(atomic_site.atom)


if __name__ == '__main__':
    TestCrystalBase.execute_all()