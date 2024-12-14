import tempfile

from tests.base_pattern import ParserBaseTest
from xrdpattern.parsing import Orientation
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
        primary_wavelength = metadata.primary_wavelength
        secondary_wavelength = metadata.secondary_wavelength

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
        patterns = self.parser.extract(fpath=DataExamples.get_xlsx_fpath(), csv_orientation=Orientation.VERTICAL)
        for p in patterns:
            self.assertIsInstance(p, XrdData)

    def test_multi_csv(self):
        patterns = self.parser.extract(fpath=DataExamples.get_multi_csv_fpath(), csv_orientation=Orientation.VERTICAL)
        for p in patterns:
            self.assertIsInstance(p, XrdData)

    def test_dat(self):
        patterns = self.parser.extract(fpath=DataExamples.get_dat_fpath())
        for p in patterns:
            self.assertIsInstance(p, XrdData)


class TestParserDatabase(ParserBaseTest):
    def test_db_parsing_ok(self):
        with self.assertNoLogs(level=0):
            bruker_db = self.get_bruker_db()
            all_db = self.get_all_db()

        for db in [bruker_db, all_db]:
            self.assertIsInstance(db, PatternDB)
        all_db.save(dirpath=tempfile.mktemp())

    @staticmethod
    def get_bruker_db() -> PatternDB:
        return PatternDB.load(dirpath=DataExamples.get_datafolder_fpath())
        
    @staticmethod
    def get_all_db() -> PatternDB:
        return PatternDB.load(dirpath=DataExamples.get_example_dirpath(), csv_orientation=Orientation.VERTICAL)



if __name__ == "__main__":
    # TestParserDatabase.execute_all()
    TestCustomFormats.execute_all()