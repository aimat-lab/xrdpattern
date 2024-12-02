import tempfile

from tests.base_tests import ParserBaseTest
from xrdpattern.parsing import Orientation, DataExamples
from xrdpattern.pattern import XrdPattern, PatternDB


# -----------------------------------------------------------------

class TestMasterParser(ParserBaseTest):
    @classmethod
    def get_fpath(cls) -> str:
        return DataExamples.get_bruker_fpath()

    def test_obj_ok(self):
        self.assertIsInstance(self.pattern, XrdPattern)
        print(f'serialized pattern')
        print(f'{self.pattern.to_str()[:1000]} + {self.pattern.to_str()[-1000:]}')

    def test_report_ok(self):
        report = self.pattern.get_parsing_report(datafile_fpath=self.get_fpath())
        as_str = report.as_str()
        self.assertIsInstance(obj=as_str, cls=str)
        print(f'Parsing report: {as_str}')

    def test_metadata_ok(self):
        metadata = self.pattern.powder_experiment
        primary_wavelength = metadata.primary_wavelength
        secondary_wavelength = metadata.secondary_wavelength
        print(f'prim, sec, ratio {primary_wavelength}, {secondary_wavelength}')

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


class TestParseStoe(ParserBaseTest):
    @classmethod
    def get_fpath(cls) -> str:
        return DataExamples.get_stoe_fpath()

    def test_parse_stoe(self):
        pattern = XrdPattern.load(fpath=self.get_fpath())
        self.assertIsInstance(pattern, XrdPattern)
        print(f'serialized pattern')
        print(f'{pattern.to_str()[:1000]} ... {pattern.to_str()[-1000:]}')


class TestParserDatabase(ParserBaseTest):

    def test_db_parsing_ok(self):
        with self.assertNoLogs(level=0):
            bruker_db = self.get_bruker_db()
            all_db = self.get_all_db()

        for db in [bruker_db, all_db]:
            self.assertIsInstance(db, PatternDB)
        all_db.save(dirpath=tempfile.mktemp())


    def test_db_report_ok(self):
        bruker_db = self.get_bruker_db()
        all_db = self.get_all_db()

        for db in [bruker_db, all_db]:
            report = db.database_report
            as_str = report.as_str()
            print(f'Parsing report: {as_str[:300]}')

            self.assertIsInstance(obj=as_str, cls=str)
            self.assertTrue(len(report.pattern_reports) > 0)


    @staticmethod
    def get_bruker_db() -> PatternDB:
        return PatternDB.load(dirpath=DataExamples.get_datafolder_fpath())
        
    @staticmethod
    def get_all_db() -> PatternDB:
        return PatternDB.load(dirpath=DataExamples.get_example_dirpath(), csv_orientation=Orientation.HORIZONTAL)



if __name__ == "__main__":
    # TestParserDatabase.execute_all()
    # TestMasterParser.update_aimat_json()
    TestParserDatabase.execute_all()