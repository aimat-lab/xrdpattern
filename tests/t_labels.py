from holytools.devtools import Unittest
from pymatgen.core import Lattice

from xrdpattern.crystal import CrystalStructure, CrystalBasis
from xrdpattern.xrd import PowderExperiment, XrayInfo
from xrdpattern.xrd.experiment import ExperimentTensor, LabelType
from xrdpattern.crystal.examples import CrystalExamples

class TestPowderExperiment(Unittest):
    def setUp(self):
        cif_content = CrystalExamples.get_cif_content(num=1)
        self.empty_experiment : PowderExperiment = PowderExperiment.make_empty()
        self.full_experiment : PowderExperiment = PowderExperiment.from_cif(cif_content=cif_content)
        self.full_experiment.primary_phase.calculate_properties()

    def test_is_empty(self):
        empty_experiment = PowderExperiment.make_empty()
        self.assertTrue(not empty_experiment.is_labeled())
        self.assertTrue(self.full_experiment.is_labeled())

    def test_has_label(self):
        self.assertTrue(not self.empty_experiment.has_label(label_type=LabelType.lattice))

        self.assertTrue(self.full_experiment.has_label(label_type=LabelType.lattice))
        self.assertTrue(self.full_experiment.has_label(label_type=LabelType.atom_coords))
        self.assertTrue(self.full_experiment.has_label(label_type=LabelType.spg))


class TestTensorization(Unittest):
    def setUp(self):
        self.label : PowderExperiment = self.make_example_label()
        self.crystal_structure: CrystalStructure = self.label.phases[0]
        self.experiment_tensor : ExperimentTensor = self.label.to_tensordict()

    def test_lattice_params(self):
        expected = (*self.crystal_structure.lengths, *self.crystal_structure.angles)
        actual = self.experiment_tensor.get_lattice_params().tolist()
        print(f'Tensor lattice params are {actual}')
        for x,y in zip(expected, actual):
            self.assertEqual(x, y)

    def test_spacegroups(self):
        expected = [1.0 if j ==  self.crystal_structure.spacegroup else 0.0 for j in range(1,231)]
        actual = self.experiment_tensor.get_spg_probabilities().tolist()
        print(f'Tensor spacegroups probabilities are {actual}; \nSpacegroups tensor length = {len(actual)}')
        self.assertEqual(actual, expected, f'Expected: {expected}, Actual: {actual}')
        self.assertEqual(len(actual), 230)

    def test_wavelength(self):
        expected = self.label.xray_info.primary_wavelength
        actual = self.experiment_tensor.get_primary_wavelength()
        print(f'Tensor primary wavelength is {actual}')
        self.assertAlmostEqual(actual, expected)

        expected_secondary = self.label.xray_info.secondary_wavelength
        actual_secondary = self.experiment_tensor.get_secondary_wavelength()
        print(f'Tensor secondary wavelength is {actual_secondary}')
        self.assertAlmostEqual(actual_secondary, expected_secondary)

    @staticmethod
    def make_example_label() -> PowderExperiment:
        lattice = Lattice.from_parameters(3,3,3,90,90,90)
        basis = CrystalBasis.empty()
        crystal_structure = CrystalStructure(lattice=lattice, basis=basis)
        crystal_structure.spacegroup = 120

        xray_info = XrayInfo.copper_xray()
        return PowderExperiment(phases=[crystal_structure], xray_info=xray_info, crystallite_size_nm=10, temp_K=300)

if __name__ == "__main__":
    TestPowderExperiment.execute_all()
    # TestTensorization.execute_all()