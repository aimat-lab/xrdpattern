from xrdpattern.pattern import XrdPattern
from xrdpattern.database import PatternDB
from t_nexus.base import PatternBaseTest, ParserBaseTest


class TestParserPattern(PatternBaseTest):
    def get_fpath(self) -> str:
        return self.get_bruker_fpath()

    def test_obj_ok(self):
        self.assertIsInstance(self.pattern, XrdPattern)
        print(f'serialized pattern')
        print(f'{self.pattern.to_str()[:1000]} + {self.pattern.to_str()[-1000:]}')

    def test_report_ok(self):
        report = self.pattern.get_parsing_report()
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

        print(f'filepath : {self.pattern.datafile_path}')
        print(f'name : {self.pattern.get_name()}')
        self.assertIsNotNone(obj=self.pattern.datafile_path)
        self.assertIsNotNone(obj=self.pattern.get_name())
        self.assertEqual(first=self.get_fpath(), second=self.pattern.datafile_path)

    def test_data_ok(self):
        raw_data = self.pattern.get_data(apply_standardization=False)
        std_data = self.pattern.get_data(apply_standardization=True)
        for data in [raw_data, std_data]:
            self.check_data_ok(data=data)

    def save(self):
        self.pattern.save(fpath='/home/daniel/local/misc/example_files/aimat.json')

class TestParserDatabase(ParserBaseTest):
    def setUp(self):
        self.pattern_db = PatternDB.load(datafolder_path=self.get_datafolder_fpath())

    def test_obj_ok(self):
        self.assertIsInstance(self.pattern_db, PatternDB)

    def test_report_ok(self):
        report = self.pattern_db.database_report
        as_str = report.get_str()
        print(f'Parsing report: {as_str}')

        self.assertIsInstance(obj=as_str, cls=str)
        self.assertTrue(len(report.pattern_reports) > 0)


class TestParseStoe(PatternBaseTest):
    def get_fpath(self) -> str:
        return self.get_stoe_fpath()

if __name__ == "__main__":
    TestParserPattern.execute_all(manual_mode=False)
    TestParserDatabase.execute_all(manual_mode=False)