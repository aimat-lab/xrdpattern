import os.path
from xrdpattern.pattern import XrdPattern
from xrdpattern.parsing import Formats
from tests.base_tests import PatternBaseTest

import tempfile


class TestXrdPattern(PatternBaseTest):
    @classmethod
    def get_fpath(cls) -> str:
        return cls.get_aimat_xrdpattern_fpath()

    def test_save_load_roundtrip(self):
        pattern = XrdPattern.load(fpath=self.get_bruker_fpath())
        pattern_str = pattern.to_str()
        save_path = os.path.join(tempfile.mkdtemp(), f'pattern.{Formats.xrdpattern.suffix}')
        pattern.save(fpath=save_path)
        pattern2 = XrdPattern.load(fpath=save_path)
        self.assertEqual(first=pattern, second=pattern2)
        print(f'pattern after roundtrip {pattern[:500]} + {pattern[-500:]}')

    def test_plot(self):
        if self.is_manual_mode:
            self.skipTest(reason='Only available in manual mode')

    def test_standardize(self):
        pattern = self.pattern
        two_theta_values, _ = pattern.get_pattern_data(apply_standardization=True)
        self.assertTrue(len(two_theta_values) == XrdPattern.get_std_num_entries())

    def test_data_ok(self):
        raw_data = self.pattern.get_pattern_data(apply_standardization=False)
        std_data = self.pattern.get_pattern_data(apply_standardization=True)
        for data in [raw_data, std_data]:
            self.check_data_ok(*data)

    def test_from_angle_data(self):
        angles = [1.0, 2.0, 3.0]
        intensities = [10.0, 20.0, 100.0]
        pattern = XrdPattern.make_unlableed(two_theta_values=angles, intensities=intensities)
        self.check_data_ok(*pattern.get_pattern_data(apply_standardization=False))

if __name__ == "__main__":
    TestXrdPattern.execute_all(manual_mode=False)



