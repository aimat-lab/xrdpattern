from holytools.devtools import Unittest
from xrdpattern.parsing.csv import CsvParser
from xrdpattern.parsing.csv.matrix import CsvOrientations
from xrdpattern.parsing.examples import DataExamples


class TestCsvReader(Unittest):
    def setUp(self):
        self.vertical_csv_path = DataExamples.get_vertical_csv_fpath()
        self.horizontal_csv_path = DataExamples.get_horizontal_fpath()
        self.single_csv_path = DataExamples.get_single_csv_fpath()

        self.multi_first_datarow = [0.322219,0.22494,0.116506,0.14788,0.161613,0.229082]
        self.single_first_datarow = [232.0, 185.0, 227.0, 216.0, 199.0, 227.0]

    def test_read_csv_vertical(self):
        csv_orientation = CsvOrientations.VERTICAL
        self.read_as_matrix(csv_orientation, self.vertical_csv_path)
        self.read_as_pattern_info(CsvOrientations.VERTICAL, self.vertical_csv_path)

    def test_read_csv_horizontal(self):
        self.read_as_matrix(CsvOrientations.HORIZONTAL, self.horizontal_csv_path)
        self.read_as_pattern_info(CsvOrientations.HORIZONTAL, self.horizontal_csv_path)

    def test_read_csv_single(self):
        self.read_as_matrix(CsvOrientations.VERTICAL, self.single_csv_path)
        self.read_as_pattern_info(CsvOrientations.VERTICAL, self.single_csv_path)

    def read_as_matrix(self, pattern_data_axis : str, csv_path : str):
        reader = CsvParser()
        table = reader._as_matrix(fpath=csv_path, pattern_orientation=pattern_data_axis)
        expected_set = set(self.single_first_datarow) if csv_path == self.single_csv_path else set(self.multi_first_datarow)
        actual_set = set(table.get_y_data(row=1))
        print(f'Actual, expected row: \n{actual_set} \n{expected_set}')

        self.assertTrue(expected_set.issubset(actual_set))

    @staticmethod
    def read_as_pattern_info(pattern_data_axis : str, csv_path : str):
        reader = CsvParser()
        reader.extract_multi(fpath=csv_path, pattern_dimension=pattern_data_axis)


if __name__ == '__main__':
    TestCsvReader.execute_all()
