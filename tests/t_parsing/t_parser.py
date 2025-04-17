import tempfile
from typing import Optional

from holytools.devtools import Unittest
from tests.base_pattern import ParserBaseTest
from xrdpattern.parsing import Formats
from xrdpattern.parsing.csv.matrix import CsvOrientations
from xrdpattern.parsing.examples import DataExamples
from xrdpattern.pattern import XrdPattern, PatternDB
from xrdpattern.xrd import XrdData

# -----------------------------------------------------------------

class TestXYLib(ParserBaseTest):
    @classmethod
    def get_fpath(cls) -> str:
        return DataExamples.get_bruker_fpath()

    def test_obj_ok(self):
        self.assertIsInstance(self.pattern, XrdPattern)

    def test_metadata_ok(self):
        metadata = self.pattern.powder_experiment
        primary_wavelength = metadata.xray_info.primary_wavelength
        secondary_wavelength = metadata.xray_info.secondary_wavelength

        for prop in [primary_wavelength, secondary_wavelength]:
            self.assertIsNotNone(obj=prop)

    def test_data_ok(self):
        raw_data = self.pattern.get_pattern_data(apply_standardization=False)
        std_data = self.pattern.get_pattern_data(apply_standardization=True)
        for data in [raw_data, std_data]:
            self.check_data_ok(*data)

    @classmethod
    def update_aimat_json(cls):
        pattern = XrdPattern.load(fpath=cls.get_fpath())
        pattern.save(fpath=DataExamples.get_aimat_fpath(), force_overwrite=True)


class TestCustomFormats(ParserBaseTest):
    def test_parse_stoe(self):
        pattern = XrdPattern.load(fpath=DataExamples.get_stoe_fpath())
        self.assertIsInstance(pattern, XrdPattern)

    def test_single_csv(self):
        pattern = XrdPattern.load(fpath=DataExamples.get_single_csv_fpath())
        self.assertIsInstance(pattern, XrdPattern)

    def test_cif(self):
        pattern = XrdPattern.load(fpath=DataExamples.get_cif_fpath())
        self.assertIsInstance(pattern, XrdPattern)

    def test_xlsx(self):
        patterns = self.parser.extract(fpath=DataExamples.get_xlsx_fpath(), csv_orientation=CsvOrientations.VERTICAL)
        for p in patterns:
            self.assertIsInstance(p, XrdData)

    def test_horizontal_csv(self):
        patterns = self.parser.extract(fpath=DataExamples.get_horizontal_fpath(), csv_orientation=CsvOrientations.HORIZONTAL)
        for p in patterns:
            self.assertIsInstance(p, XrdData)

    def test_dat(self):
        patterns = self.parser.extract(fpath=DataExamples.get_dat_fpath())
        for p in patterns:
            self.assertIsInstance(p, XrdData)

original_get_fpaths = Formats.get_xrd_fpaths
def load_excluding_horizontal(dirpath : str, selected_suffixes : Optional[list[str]]):
    xrd_fpaths = original_get_fpaths(dirpath=dirpath, selected_suffixes=selected_suffixes)
    xrd_fpaths = [fpath for fpath in xrd_fpaths if not 'horizontal' in fpath]
    return xrd_fpaths

class TestParserDatabase(ParserBaseTest):
    @Unittest.patch_module(original=Formats.get_xrd_fpaths, replacement=load_excluding_horizontal)
    def test_db_parsing_ok(self):
        all_db = PatternDB.load(dirpath=DataExamples.get_example_dirpath(), csv_orientation=CsvOrientations.VERTICAL, strict=True)
        all_db.save(dirpath=tempfile.mktemp())
        self.assertIsInstance(all_db, PatternDB)


if __name__ == "__main__":
    TestParserDatabase.execute_all()
    # TestCustomFormats.execute_all()