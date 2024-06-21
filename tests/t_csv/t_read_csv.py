import os
from xrdpattern.parsing.csv import Orientation, CsvParser
from holytools.devtools import Unittest

class TestCsvReader(Unittest):

    def setUp(self):
        # Setup CsvReader with comma as a separator
        test_dirpath = os.path.dirname(os.path.abspath(__file__))
        self.vertical_csv_path = os.path.join(test_dirpath,'vertical.csv')
        self.horizontal_csv_path = os.path.join(test_dirpath,'horizontal.csv')
        self.multi_first_row = [0.3926,0.322219,0.255273,0.531479,0.518514,0.518514,0.612784]

        self.single_csv_path = os.path.join(test_dirpath, 'single.csv')
        self.single_first_row = [30.00313028, 30.029390845, 30.05565141, 30.081911975, 30.10817254, 30.134433105, 30.16069367, 30.186954235, 30.2132148]


    def test_read_csv_vertical(self):
        self.read_as_matrix(Orientation.VERTICAL, self.vertical_csv_path)
        self.read_as_pattern_info(Orientation.VERTICAL, self.vertical_csv_path)

    def test_read_csv_horizontal(self):
        self.read_as_matrix(Orientation.HORIZONTAL, self.horizontal_csv_path)
        self.read_as_pattern_info(Orientation.HORIZONTAL, self.horizontal_csv_path)

    def test_read_csv_single(self):
        self.read_as_matrix(Orientation.VERTICAL, self.single_csv_path)
        self.read_as_pattern_info(Orientation.VERTICAL, self.single_csv_path)

    def read_as_matrix(self, pattern_data_axis : Orientation, csv_path : str):
        reader = CsvParser()
        table = reader._as_matrix(fpath=csv_path, pattern_orientation=pattern_data_axis)
        expected_set = set(self.single_first_row) if csv_path==self.single_csv_path else set(self.multi_first_row)
        actual_set = set(table.data[0])
        print(f'Actual, expected row: \n{actual_set} \n{expected_set}')

        self.assertTrue(expected_set.issubset(actual_set))

    @staticmethod
    def read_as_pattern_info(pattern_data_axis : Orientation, csv_path : str):
        reader = CsvParser()
        reader.extract_patterns(fpath=csv_path, pattern_dimension=pattern_data_axis)


if __name__ == '__main__':
    TestCsvReader.execute_all()
