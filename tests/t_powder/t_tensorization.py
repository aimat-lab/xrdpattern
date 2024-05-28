from holytools.devtools import Unittest
from xrdpattern.powder import PowderExperiment, Powder, CrystalStructure, AtomicSite, PowderTensor, Lengths, Angles, \
    CrystalBase, Artifacts


class TestTensorRegions(Unittest):
    def setUp(self):
        self.experiment = self.make_example_experiment()
        self.powder_tensor : PowderTensor = self.experiment.to_tensor()
        self.crystal_structure : CrystalStructure = self.experiment.powder.crystal_structure


    def test_lattice_params(self):
        expected = (*self.crystal_structure.lengths, *self.crystal_structure.angles)
        actual = self.powder_tensor.get_lattice_params().tolist()
        print(f'Tensor lattice params are {actual}')
        for x,y in zip(expected, actual):
            self.assertEqual(x, y)


    def test_atomic_sites(self):
        base = self.crystal_structure.base
        for i, region in enumerate(self.experiment.atomic_site_regions):
            expected_site = base[i] if i < len(base) else AtomicSite.make_void()
            expected = expected_site.as_list()
            actual = self.powder_tensor.get_atomic_site(i).tolist()
            if i == 0:
                print(f'Tensor atomic site is {actual}\n Atomic site length = {len(actual)}')
            # 3 coordinates, 8 scattering params, 1 occupancy
            self.assertEqual(len(actual), 3+8+1)
            for x,y, in zip(expected, actual):
                if self.is_nan(x):
                    self.assertTrue(self.is_nan(y))
                else:
                    self.assertEqual(x,y)

    def test_spacegroups(self):
        expected = [j ==  self.crystal_structure.space_group for j in range(1,231)]
        actual = self.powder_tensor.get_spacegroups().tolist()
        print(f'Tensor spacegroups are {actual}; \nSpacegroups tensor length = {len(actual)}')
        self.assertEqual(actual, expected, f'Expected: {expected}, Actual: {actual}')
        self.assertEqual(len(actual), 230)


    def test_artifacts(self):
        expected = [round(num, 2) for num in self.experiment.artifacts.as_list()]
        actual = [round(num, 2) for num in self.powder_tensor.get_artifacts().tolist()]
        print(f'Tensor artifacts are {actual}')
        self.assertEqual(actual, expected)

    def test_total_length(self):
        expected = len(self.experiment.list_repr)
        # noinspection PyTypeChecker
        actual = len(self.powder_tensor)
        print(f'Tensor length is {actual}')
        self.assertEqual(actual, expected)


    def test_returns_powder_tensors(self):
        tensors = [self.powder_tensor.get_atomic_site(0), self.powder_tensor.get_lattice_params(), self.powder_tensor.get_lattice_params()]
        for t in tensors:
            print(f'Type of {t} is {type(t)}')
            self.assertEqual(t.__class__, PowderTensor)

    @staticmethod
    def make_example_experiment() -> PowderExperiment:
        primitives = Lengths(a=3, b=3, c=3)
        angles = Angles(alpha=90, beta=90, gamma=90)
        base = CrystalBase([AtomicSite.make_void()])
        crystal_structure = CrystalStructure(lengths=primitives, angles=angles, base=base)
        crystal_structure.space_group = 120

        powder = Powder(crystal_structure=crystal_structure, crystallite_size=10.0)
        artifacts = Artifacts(primary_wavelength=1.54, secondary_wavelength=1.54, secondary_to_primary=0.5)
        return PowderExperiment(powder, artifacts, is_simulated=True)

    @staticmethod
    def is_nan(value):
        return value != value

if __name__ == "__main__":
    TestTensorRegions.execute_all()
