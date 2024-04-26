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
        self.assertTrue(len(intensity_map.data) == XrdPattern.get_std_num_entries())

    def test_convert_axis(self):
        wavelength = 1.54
        pattern = self.pattern
        new_data = pattern.xrd_intensities.as_qvalues_map(wavelength=wavelength)
        # print(new_data.to_str())
        print(len(new_data.data))
        self.check_data_ok(data=new_data)

    def test_data_ok(self):
        raw_data = self.pattern.get_data(apply_standardization=False)
        std_data = self.pattern.get_data(apply_standardization=True)
        for data in [raw_data, std_data]:
            self.check_data_ok(data=data)


if __name__ == "__main__":
    TestXrdPattern.execute_all(manual_mode=False)



