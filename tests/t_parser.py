import os.path

from xrdpattern.pattern import XrdPattern
from xrdpattern.database import PatternDB
from tests.base import PatternBaseTest, ParserBaseTest


class TestParserPattern(PatternBaseTest):
    def get_fpath(self) -> str:
        return self.get_bruker_fpath()

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
        metadata = self.pattern.metadata
        properties = [metadata.anode_material, metadata.measurement_date]
        print(f'anode material {metadata.anode_material}')
        print(f'measurement date {metadata.measurement_date}')

        for prop in properties:
            self.assertIsNotNone(obj=prop)

        primary_wavelength = metadata.primary
        secondary_wavelength = metadata.secondary
        ratio = metadata.ratio
        print(f'prim, sec, ratio {primary_wavelength}, {secondary_wavelength}, {ratio}')

        for prop in [primary_wavelength, secondary_wavelength, ratio]:
            self.assertIsNotNone(obj=prop)

        print(f'name : {self.pattern.get_name()}')
        self.assertIsNotNone(obj=self.pattern.get_name())
        original_name = os.path.basename(self.get_fpath())
        self.assertIn(self.pattern.get_name(), original_name)

    def test_data_ok(self):
        raw_data = self.pattern.get_data(apply_standardization=False)
        std_data = self.pattern.get_data(apply_standardization=True)
        for data in [raw_data, std_data]:
            self.check_data_ok(data=data)

    def save(self):
        self.pattern.save(fpath='/home/daniel/local/misc/example_files/aimat.json')


class TestParseStoe(PatternBaseTest):
    def get_fpath(self) -> str:
        return self.get_stoe_fpath()


class TestParserDatabase(ParserBaseTest):
    def test_db_ok(self):
        import logging
        logger_dict = logging.root.manager.loggerDict
        logger =  list(logger_dict.keys())
        print(f'logger {logger}')

        with self.assertNoLogs(level=0):
            self.bruker_only_db = PatternDB.load(datafolder_path=self.get_datafolder_fpath())
            self.all_example_db = PatternDB.load(datafolder_path=self.get_example_folderpath())

        for db in [self.bruker_only_db, self.all_example_db]:
            self.assertIsInstance(db, PatternDB)

        for db in [self.bruker_only_db, self.all_example_db]:
            report = db.database_report
            as_str = report.get_str()
            print(f'Parsing report: {as_str[:300]}')

            self.assertIsInstance(obj=as_str, cls=str)
            self.assertTrue(len(report.pattern_reports) > 0)


if __name__ == "__main__":
    # TestParserDatabase.execute_all(manual_mode=False)

    PatternDB.load(datafolder_path=PatternBaseTest.get_example_folderpath())

