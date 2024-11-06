from xrdpattern.crystal import CrystalStructure, Lengths, Angles, CrystalBase, AtomicSite
from holytools.devtools import Unittest
from xrdpattern.xrd import PowderExperiment, PowderSample, Artifacts, LabelTensor


class TestTensorRegions(Unittest):
    def setUp(self):
        self.label : PowderExperiment = self.make_example_label()
        self.label_tensor : LabelTensor = self.label.to_tensor()
        self.crystal_structure : CrystalStructure = self.label.powder.crystal_structure


    def test_lattice_params(self):
        expected = (*self.crystal_structure.lengths, *self.crystal_structure.angles)
        actual = self.label_tensor.get_lattice_params().tolist()
        print(f'Tensor lattice params are {actual}')
        for x,y in zip(expected, actual):
            self.assertEqual(x, y)


    def test_atomic_sites(self):
        base = self.crystal_structure.base
        for i, region in enumerate(self.label.atomic_site_regions):
            expected_site = base[i] if i < len(base) else AtomicSite.make_void()
            expected = expected_site.as_list()
            actual = self.label_tensor.get_atomic_site(i).tolist()
            if i == 0:
                print(f'Tensor atomic site is {actual}\n Atomic site length = {len(actual)}')
            # 3 coordinates, 8 scattering params, 1 occupancy
            self.assertEqual(len(actual), 3+8+1)
            for x,y, in zip(expected, actual):
                if x is None:
                    self.assertTrue(is_nan(y))
                else:
                    self.assertEqual(x,y)

    def test_spacegroups(self):
        expected = [1.0 if j ==  self.crystal_structure.spacegroup else 0.0 for j in range(1,231)]
        actual = self.label_tensor.get_spg_probabilities().tolist()
        print(f'Tensor spacegroups are {actual}; \nSpacegroups tensor length = {len(actual)}')
        self.assertEqual(actual, expected, f'Expected: {expected}, Actual: {actual}')
        self.assertEqual(len(actual), 230)


    def test_artifacts(self):
        expected = [round(num, 2) for num in self.label.artifacts.as_list()]
        actual = [round(num, 2) for num in self.label_tensor.get_artifacts().tolist()]
        print(f'Tensor artifacts are {actual}')
        self.assertEqual(actual, expected)

    def test_total_length(self):
        expected = len(self.label.list_repr)
        # noinspection PyTypeChecker
        actual = len(self.label_tensor)
        print(f'Tensor length is {actual}')
        self.assertEqual(actual, expected)


    def test_returns_powder_tensors(self):
        tensors = [self.label_tensor.get_atomic_site(0), self.label_tensor.get_lattice_params(), self.label_tensor.get_lattice_params()]
        for t in tensors:
            print(f'Type of {t} is {type(t)}')
            self.assertEqual(t.__class__, LabelTensor)

    @staticmethod
    def make_example_label() -> PowderExperiment:
        primitives = Lengths(a=3, b=3, c=3)
        angles = Angles(alpha=90, beta=90, gamma=90)
        base = CrystalBase([AtomicSite.make_void()])
        crystal_structure = CrystalStructure(lengths=primitives, angles=angles, base=base)
        crystal_structure.spacegroup = 120

        powder = PowderSample(crystal_structure=crystal_structure, crystallite_size=10.0)
        artifacts = Artifacts(primary_wavelength=1.54, secondary_wavelength=1.54)
        return PowderExperiment(powder, artifacts, is_simulated=True)


def is_nan(value):
    return value != value

if __name__ == "__main__":
    TestTensorRegions.execute_all()