import os.path

from xrdpattern.pattern import XrdPattern
from hollarek.devtools import Unittest
import tempfile

class TestXrdPattern(Unittest):
    def setUp(self):
        this_file_path = os.path.abspath(__file__)
        this_dir_path = os.path.dirname(this_file_path)
        self.pattern_fpath = os.path.join(this_dir_path, 'pattern.json')

    def test_save_load_roundtrip(self):
        pattern = XrdPattern.load(fpath=self.pattern_fpath)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp_file:
            temp_file_path = tmp_file.name

        self.pattern_fpath = temp_file_path
        pattern.save(fpath=self.pattern_fpath)
        pattern2 = XrdPattern.load(fpath=self.pattern_fpath)
        self.assertEqual(first=pattern, second=pattern2)
        print(f'pattern after roundtrip {pattern.to_str()}')

    # def test_plot(self):
    #
    # 
    #
    # def test_standardize(self):
    #
    #
    # def test_convert_axis(self):


if __name__ == "__main__":
    TestXrdPattern.execute_all()