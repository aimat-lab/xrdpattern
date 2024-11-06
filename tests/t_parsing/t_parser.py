import os.path

from xrdpattern.parsing import Orientation, DataExamples
from xrdpattern.pattern import XrdPattern, PatternDB
from tests.base_tests import ParserBaseTest


# -----------------------------------------------------------------

class TestParserPattern(ParserBaseTest):
    @classmethod
    def get_fpath(cls) -> str:
        return DataExamples.get_bruker_fpath()

    def test_obj_ok(self):
        self.assertIsInstance(self.pattern, XrdPattern)
        print(f'serialized pattern')
        print(f'{self.pattern.to_str()[:1000]} + {self.pattern.to_str()[-1000:]}')

    def test_report_ok(self):
        report = self.pattern.get_parsing_report(datafile_fpath=self.get_fpath())
        as_str = report.get_report_str()
        self.assertIsInstance(obj=as_str, cls=str)
        print(f'Parsing report: {as_str}')

    def test_metadata_ok(self):
        metadata = self.pattern.label
        primary_wavelength = metadata.primary_wavelength
        secondary_wavelength = metadata.secondary_wavelength
        print(f'prim, sec, ratio {primary_wavelength}, {secondary_wavelength}')

        for prop in [primary_wavelength, secondary_wavelength]:
            self.assertIsNotNone(obj=prop)

        print(f'name : {self.pattern.get_name()}')
        self.assertIsNotNone(obj=self.pattern.get_name())
        original_name = os.path.basename(self.get_fpath())
        self.assertIn(self.pattern.get_name(), original_name)

    def test_data_ok(self):
        raw_data = self.pattern.get_pattern_data(apply_standardization=False)
        std_data = self.pattern.get_pattern_data(apply_standardization=True)
        for data in [raw_data, std_data]:
            self.check_data_ok(*data)


class TestParseStoe(ParserBaseTest):
    @classmethod
    def get_fpath(cls) -> str:
        return DataExamples.get_stoe_fpath()

    def test_parse_stoe(self):
        pattern = XrdPattern.load(fpath=self.get_fpath())
        self.assertIsInstance(pattern, XrdPattern)
        print(f'serialized pattern')
        print(f'{pattern.to_str()[:1000]} ... {pattern.to_str()[-1000:]}')


from unittest.mock import patch
class TestParserDatabase(ParserBaseTest):
    bruker_only_db = None
    all_example_db = None

    @patch('builtins.input', lambda *args, **kwargs : 'VERTICAL')
    def test_db_parsing_ok(self):
        with self.assertNoLogs(level=0):
            TestParserDatabase.bruker_only_db = PatternDB.load(dirpath=DataExamples.get_datafolder_fpath())
            TestParserDatabase.all_example_db = PatternDB.load(dirpath=DataExamples.get_example_dirpath(),
                                                               default_csv_orientation=Orientation.HORIZONTAL)

        for db in [self.bruker_only_db, self.all_example_db]:
            self.assertIsInstance(db, PatternDB)
        self.all_example_db.save(dirpath='/tmp/patterndb')


    def test_db_report_ok(self):
        for db in [self.bruker_only_db, self.all_example_db]:
            report = db.database_report
            as_str = report.get_str()
            print(f'Parsing report: {as_str[:300]}')

            self.assertIsInstance(obj=as_str, cls=str)
            self.assertTrue(len(report.pattern_reports) > 0)


if __name__ == "__main__":
    # TestParserDatabase.execute_all(manual_mode=False)
    # TestParserPattern.execute_all()
    # TestParseStoe.execute_all()
    # TestParserPattern.execute_all()
    # pattern = XrdPattern.load(fpath='/home/daniel/Drive/data/opxrd/v0_backup/breitung_schweidler_0/data/Yanyan/HEALF/CoCrFeMnNi.raw')

    # _ = PatternDB.load(dirpath='/home/daniel/Drive/data/opxrd/v0_backup/breitung_schweidler_0/')
    TestParserDatabase.execute_all()
    TestParseStoe.execute_all()
    TestParserPattern.execute_all()