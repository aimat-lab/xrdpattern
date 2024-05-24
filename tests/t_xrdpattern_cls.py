import os.path
from xrdpattern.pattern import XrdPattern
from tests.base_tests import PatternBaseTest

import tempfile


class TestXrdPattern(PatternBaseTest):
    def get_fpath(self) -> str:
        return self.get_aimat_json_fpath()

    def test_save_load_roundtrip(self):
        pattern = self.pattern
        save_path = os.path.join(tempfile.mkdtemp(), 'pattern.json')
        pattern.save(fpath=save_path)
        pattern2 = XrdPattern.load(fpath=save_path)
        self.assertEqual(first=pattern, second=pattern2)
        print(f'pattern after roundtrip {pattern.to_str()[:500]} + {pattern.to_str()[-500:]}')

    def test_plot(self):
        if self.is_manual_mode:
            self.skipTest(reason='Only available in manual mode')

    def test_standardize(self):
        pattern = self.pattern
        intensity_map =pattern.get_data(apply_standardization=True)
        self.assertTrue(len(intensity_map.twotheta_mapping) == XrdPattern.get_std_num_entries())

    def test_data_ok(self):
        raw_data = self.pattern.get_data(apply_standardization=False)
        std_data = self.pattern.get_data(apply_standardization=True)
        for data in [raw_data, std_data]:
            self.check_data_ok(data=data)

    def test_from_angle_data(self):
        angles = [1.0, 2.0, 3.0]
        intensities = [10.0, 20.0, 100.0]
        pattern = XrdPattern.from_angle_map(angles=angles, intensities=intensities)
        self.check_data_ok(data=pattern.xrd_intensities)

if __name__ == "__main__":
    TestXrdPattern.execute_all(manual_mode=False)



