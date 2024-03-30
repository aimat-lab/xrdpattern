import os.path
from tests.basetest import PatternBaseTest
from xrdpattern.pattern import XrdPattern
import tempfile


class TestXrdPattern(PatternBaseTest):
    def get_fpath(self) -> str:
        this_file_path = os.path.abspath(__file__)
        this_dir_path = os.path.dirname(this_file_path)
        fpath = os.path.join(this_dir_path, 'pattern.json')
        return fpath


    def test_save_load_roundtrip(self):
        pattern = self.pattern
        save_path = os.path.join(tempfile.mkdtemp(), 'pattern.json')
        pattern.save(fpath=save_path)
        pattern2 = XrdPattern.load(fpath=save_path)
        self.assertEqual(first=pattern, second=pattern2)
        print(f'pattern after roundtrip {pattern.to_str()}')

    def test_plot(self):
        if self.is_manual_mode:
            self.skipTest(reason='Only available in manual mode')

    def test_standardize(self):
        pattern = self.pattern
        intensity_map =pattern.get_data(apply_standardization=True)
        self.assertTrue(len(intensity_map.data) == 1000)

    def test_convert_axis(self):
        wavelength = 1.54
        pattern = self.pattern
        new_data = pattern.xrd_data.as_qvalues_map(wavelength=wavelength)
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