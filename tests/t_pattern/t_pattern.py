import os.path

from xrdpattern.crystal import CrystalExamples
from xrdpattern.pattern import XrdPattern
from xrdpattern.parsing import Formats
from tests.base_tests import ParserBaseTest

from xrdpattern.parsing import DataExamples
from xrdpattern.xrd import PowderExperiment
import tempfile

# ---------------------------------------------------------

class TestXrdPattern(ParserBaseTest):
    @classmethod
    def get_fpath(cls) -> str:
        return DataExamples.get_aimat_xrdpattern_fpath()

    def test_save_load_roundtrip(self):
        unlabeled_pattern = XrdPattern.load(fpath=DataExamples.get_bruker_fpath())
        labeled_pattern = XrdPattern.load(fpath=DataExamples.get_bruker_fpath())
        labeled_pattern.label = PowderExperiment.from_cif(cif_content=CrystalExamples.get_cif_content())

        reloaded_unlabeled = self.save_and_load(unlabeled_pattern)
        reloaded_labeled = self.save_and_load(labeled_pattern)

        self.assertEqual(unlabeled_pattern, reloaded_unlabeled)
        self.assertEqual(labeled_pattern, reloaded_labeled)
        print(f'labeled after roundtrip \n:{labeled_pattern.get_info_as_str()[:500]} + '
              f'{labeled_pattern.get_info_as_str()[-500:]}')

    def test_plot(self):
        if self.is_manual_mode:
            self.skipTest(reason='Only available in manual mode')

    def test_standardize(self):
        pattern = self.pattern
        two_theta_values, _ = pattern.get_pattern_data(apply_standardization=True)
        self.assertTrue(len(two_theta_values) == XrdPattern.std_num_entries())

    def test_data_ok(self):
        raw_data = self.pattern.get_pattern_data(apply_standardization=False)
        std_data = self.pattern.get_pattern_data(apply_standardization=True)
        for data in [raw_data, std_data]:
            self.check_data_ok(*data)

    def test_from_angle_data(self):
        angles = [1.0, 2.0, 3.0]
        intensities = [10.0, 20.0, 100.0]
        pattern = XrdPattern.make_unlabeled(two_theta_values=angles, intensities=intensities)
        self.check_data_ok(*pattern.get_pattern_data(apply_standardization=False))

    @staticmethod
    def save_and_load(pattern : XrdPattern):
        save_path = os.path.join(tempfile.mkdtemp(), f'pattern.{Formats.aimat_xrdpattern.suffix}')
        pattern.save(fpath=save_path)
        reloaded_pattern = XrdPattern.load(fpath=save_path)
        return reloaded_pattern


if __name__ == "__main__":
    TestXrdPattern.execute_all()