from xrdpattern.pattern import XrdPattern
from xrdpattern.parsing import XrdParser
from hollarek.devtools import Unittest


class TestParseXrdpattern(Unittest):
    def setUp(self):
        self.data_file_path ='/home/daniel/local/pxrd/Simon_Schweidler,_Ben_Breitung_2024_02_22/data/data_kupfer/Bei/HEO-FeSb/01.06.21-NiTeMo.raw'
        self.parser = XrdParser()
        self.pattern = self.parser.get_patterns(fpath=self.data_file_path)[0]

    def test_read_ok(self):
        pattern_serialization = self.pattern.to_str()
        self.assertIsInstance(pattern_serialization, str)
        print(f'Serialized xrd pattern: {pattern_serialization}')


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
        self.assertEqual(first=self.data_file_path, second=self.pattern.datafile_path)


    def test_data_ok(self):
        data = self.pattern.get_data()
        data_str = data.to_str()
        self.assertIsInstance(data_str, str)
        print(f'Xrd data: {data_str}')
        # if self.is_manual_mode:
        #     self.pattern.plot()


if __name__ == "__main__":
    TestParseXrdpattern.execute_all()