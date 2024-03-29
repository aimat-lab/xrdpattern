from xrdpattern.pattern import XrdPattern
from xrdpattern.database import PatternDB
from xrdpattern.parsing import Parser
from hollarek.devtools import Unittest


class TestParseXrdpattern(Unittest):
    def setUp(self):
        self.data_fpath = '/home/daniel/local/pxrd/Simon_Schweidler_Ben_Breitung_2024_02_22/data/data_kupfer/Bei/HEO-FeSb/01.06.21-NiTeMo.raw'
        self.parser = Parser()
        self.pattern = XrdPattern.load(fpath=self.data_fpath)

    def test_obj_ok(self):
        self.assertIsInstance(self.pattern, XrdPattern)

        print(f'serialized pattern')
        print(f'{self.pattern.to_str()}')


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

        primary_wavelength = metadata.wavelength_info.primary
        secondary_wavelength = metadata.wavelength_info.secondary
        ratio = metadata.wavelength_info.ratio
        print(f'prim, sec, ratio {primary_wavelength}, {secondary_wavelength}, {ratio}')

        for prop in [primary_wavelength, secondary_wavelength, ratio]:
            self.assertIsNotNone(obj=prop)

        print(f'filepath : {self.pattern.datafile_path}')
        print(f'name : {self.pattern.get_name()}')
        self.assertIsNotNone(obj=self.pattern.datafile_path)
        self.assertIsNotNone(obj=self.pattern.get_name())
        self.assertEqual(first=self.data_fpath, second=self.pattern.datafile_path)


    def test_data_ok(self):
        data = self.pattern.get_data()
        data_str = data.to_str()
        self.assertIsInstance(data_str, str)
        print(f'Xrd data: {data_str}')

        keys, values = data.as_list_pair()
        for key, value in zip(keys,values):
            self.assertIsInstance(key, float)
            self.assertIsInstance(value, float)

        if self.is_manual_mode:
            self.pattern.plot()


class TestParserDatabase(Unittest):
    def setUp(self):
        self.datafolder_path : str = '/home/daniel/local/pxrd/Simon_Schweidler_Ben_Breitung_2024_02_22/data/data_kupfer/Aaditya/'
        self.pattern_db = PatternDB.load(datafolder_path=self.datafolder_path)

    def test_obj_ok(self):
        self.assertIsInstance(self.pattern_db, PatternDB)


    def test_report_ok(self):
        report = self.pattern_db.database_report
        as_str = report.get_str()
        print(f'Parsing report: {as_str}')

        self.assertIsInstance(obj=as_str, cls=str)
        self.assertTrue(len(report.pattern_reports) > 0)


if __name__ == "__main__":
    TestParseXrdpattern.execute_all(manual_mode=False)
    # TestParserDatabase.execute_all(manual_mode=False)