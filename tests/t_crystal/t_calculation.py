import math
from typing import Union

import numpy as np
from pymatgen.core import Lattice, Structure, Composition, PeriodicSite, Site, Species, Element

import tests.t_crystal.crystal_test as BaseTest
from xrdpattern.crystal import AtomicSite, CrystalStructure

# ---------------------------------------------------------

class TestPropertyCalculation(BaseTest.CrystalTest):
    def test_to_pymatgen(self):
        for struct, crystal in zip(self.pymatgen_structures, self.custom_structures):
            actual = self.to_clustered_pymatgen(crystal)
            expected = struct
            self.assertEqual(actual.lattice, expected.lattice)

            self.assertEqual(len(actual.sites), len(expected.sites))
            actual_sites = sorted(actual.sites, key=dist_from_origin)
            expected_sites = sorted(expected.sites, key=dist_from_origin)
            print(f'Expected, actual sites = {expected_sites}, {actual_sites}')
            for s1,s2 in zip(actual_sites, expected_sites):
                self.check_sites_equal(s1,s2)

            print(f'Composition = {actual.composition}')

    def test_volume(self):
        for crystal in self.custom_structures:
            crystal.calculate_properties()

        expected_volumes = [364.21601704000005, 67.96]
        for crystal, volume_exp in zip(self.custom_structures, expected_volumes):
            self.assertAlmostEqual(crystal.volume_uc, volume_exp, places=1)
        for crystal in self.custom_structures:
            print(f'self.crystal atomic volume fraction = {crystal.packing_density}')


    def test_symmetries(self):
        for crystal in self.custom_structures:
            crystal.calculate_properties()

        for crystal, space_group_exp in zip(self.custom_structures, self.spgs):
            self.assertEqual(crystal.spacegroup, space_group_exp)

        expected_systems = ['orthorhombic', 'trigonal']
        for crystal, system_exp in zip(self.custom_structures, expected_systems):
            self.assertEqual(crystal.crystal_system, system_exp)

        expected_symbols = [
            ['d', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'c', 'c', 'c', 'c', 'd', 'd', 'd', 'd'],
            ['a','a','a','b','b','b']
        ]
        for crystal, symbols_exp in zip(self.custom_structures, expected_symbols):
            self.assertEqual(crystal.wyckoff_symbols, symbols_exp)

    # ---------------------------------------------------------

    def check_sites_equal(self, s1 : Site, s2 : Site):
        s1, s2 = self.standardize_site(s1), self.standardize_site(s2)
        self.assertEqual(s1, s2)

    @staticmethod
    def standardize_site(site : Site):
        def cast_to_species(x : Union[Species, Element]):
            if isinstance(x, Element):
                x = Species(symbol=str(x), oxidation_state=0)
            return x

        if isinstance(site.species, Composition):
            comp = site.species
            species = Composition({cast_to_species(x) : occ for x, occ in comp.items()})
            site = Site(species=species, coords=site.coords)

        return site


    @staticmethod
    def to_clustered_pymatgen(crystal : CrystalStructure) -> Structure:
        a, b, c = crystal.lengths.as_tuple()
        alpha, beta, gamma = crystal.angles.as_tuple()
        lattice = Lattice.from_parameters(a, b, c, alpha, beta, gamma)

        non_void_sites = crystal.base.get_non_void_sites()

        EPSILON = 0.001
        clusters: list[list[AtomicSite]] = []

        def matching_cluster(the_site):
            for cl in clusters:
                if euclidean_dist(cl[0], the_site) < EPSILON:
                    return cl
            return None

        for site in non_void_sites:
            match = matching_cluster(site)
            if match:
                match.append(site)
            else:
                clusters.append([site])

        site_comps = []
        for clust in clusters:
            comp = Composition({site.atom.as_pymatgen : site.occupancy for site in clust})
            site_comps.append(comp)

        positions = [(c[0].x, c[0].y, c[0].z) for c in clusters]
        return Structure(lattice=lattice, species=site_comps, coords=positions)



def dist_from_origin(site : PeriodicSite | AtomicSite):
    return math.sqrt(site.x ** 2 + site.y ** 2 + site.z ** 2)

def euclidean_dist(siteA : PeriodicSite | AtomicSite, siteB: PeriodicSite | AtomicSite):
    return np.sqrt((siteA.x - siteB.x) ** 2 + (siteA.y - siteB.y) ** 2 + (siteA.z - siteB.z) ** 2)

if __name__ == '__main__':
    TestPropertyCalculation.execute_all()
