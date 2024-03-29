import os.path

from xrdpattern.core import XAxisType
from xrdpattern.pattern import XrdPattern
from hollarek.devtools import Unittest
import tempfile

class TestXrdPattern(Unittest):
    def setUp(self):
        this_file_path = os.path.abspath(__file__)
        this_dir_path = os.path.dirname(this_file_path)
        self.pattern_fpath = os.path.join(this_dir_path, 'pattern.json')

    def test_save_load_roundtrip(self):
        pattern = self.get_spoof_pattern()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp_file:
            temp_file_path = tmp_file.name

        self.pattern_fpath = temp_file_path
        pattern.save(fpath=self.pattern_fpath)
        pattern2 = XrdPattern.load(fpath=self.pattern_fpath)
        self.assertEqual(first=pattern, second=pattern2)
        print(f'pattern after roundtrip {pattern.to_str()}')

    def test_plot(self):
        if self.is_manual_mode:
            self.skipTest(reason='Only available in manual mode')

    def test_standardize(self):
        pattern = self.get_spoof_pattern()
        intensity_map =pattern.get_data(apply_standardization=True)
        self.assertTrue(len(intensity_map.data) == 1000)

    def test_convert_axis(self):
        wavelength_angstr = 1.54
        pattern = self.get_spoof_pattern()
        new_intensity = pattern.intensity_map.convert_axis(target_axis_type=XAxisType.QValues, wavelength=wavelength_angstr)
        print(new_intensity.to_str())

    def get_spoof_pattern(self) -> XrdPattern:
        return XrdPattern.load(fpath=self.pattern_fpath)


if __name__ == "__main__":
    TestXrdPattern.execute_all()