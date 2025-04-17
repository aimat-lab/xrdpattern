import os.path
import tempfile

from matplotlib import pyplot as plt

from tests.base_pattern import ParserBaseTest
from xrdpattern.crystal import CrystalExamples
from xrdpattern.parsing import Formats
from xrdpattern.parsing.examples import DataExamples
from xrdpattern.pattern import XrdPattern
from xrdpattern.xrd import PowderExperiment


# ---------------------------------------------------------

class TestXrdPattern(ParserBaseTest):
    def test_save_load_roundtrip(self):
        unlabeled_pattern = XrdPattern.load(fpath=DataExamples.get_bruker_fpath())
        labeled_pattern = XrdPattern.load(fpath=DataExamples.get_bruker_fpath())
        labeled_pattern.powder_experiment = PowderExperiment.from_cif(cif_content=CrystalExamples.get_cif_content())

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
        pattern_len = 90
        angles = [float(x) for x in range(pattern_len)]
        intensities = [float(x*20) for x in range(pattern_len)]
        pattern = XrdPattern.make_unlabeled(two_theta_values=angles, intensities=intensities)
        self.check_data_ok(*pattern.get_pattern_data(apply_standardization=False))

    def test_get_pattern_data(self):
        if not self.is_manual_mode:
            print('Only available in manual mode')
            return

        a1, i1 = self.pattern.get_pattern_data(apply_standardization=False)
        a2, i2 = self.pattern.get_pattern_data(apply_standardization=True)
        a3, i3 = self.pattern.get_pattern_data(apply_standardization=True)

        plt.figure(figsize=(15, 5))
        titles = ['Without Standardization', 'With Standardization', 'With Standardization and Constant Padding']
        data = [(a1, i1), (a2, i2), (a3, i3)]

        for idx, (angles, intensities) in enumerate(data):
            plt.subplot(1, 3, idx + 1)
            plt.plot(angles, intensities, label=titles[idx])
            plt.title(titles[idx])
            plt.xlabel('Angle (degrees)')
            plt.ylabel('Intensity')
            plt.legend()

        plt.tight_layout()
        plt.show()

    @staticmethod
    def save_and_load(pattern : XrdPattern) -> XrdPattern:
        save_path = os.path.join(tempfile.mkdtemp(), f'pattern.{Formats.aimat_suffix()}')
        pattern.save(fpath=save_path)
        reloaded_pattern = XrdPattern.load(fpath=save_path)
        return reloaded_pattern


if __name__ == "__main__":
    TestXrdPattern.execute_all()