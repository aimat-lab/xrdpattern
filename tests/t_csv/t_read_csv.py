import unittest
import os
from xrdpattern.parsing.csv import CsvReader, Orientation, CsvScheme
from xrdpattern.core import XAxisType
from hollarek.devtools import Unittest

class TestCsvReader(Unittest):

    def setUp(self):
        # Setup CsvReader with comma as a separator
        test_dirpath = os.path.dirname(os.path.abspath(__file__))
        self.vertical_csv_path = os.path.join(test_dirpath,'vertical.csv')
        self.horizontal_csv_path = os.path.join(test_dirpath,'horizontal.csv')
        self.first_row = [1.79272, 1.80218, 1.81164, 1.8211, 1.83056, 1.84002, 1.84948, 1.85894, 1.8684]

    def read_csv_and_test(self, orientation, csv_path):
        scheme = CsvScheme(pattern_dimension=orientation, x_axis_type=XAxisType.QValues)
        reader = CsvReader(scheme)
        table = reader.as_horiztontal_table(fpath=csv_path)
        expected_set = set(self.first_row)
        actual_set = set(table.data[0])
        self.assertTrue(expected_set.issubset(actual_set))

    def test_read_csv_vertical(self):
        self.read_csv_and_test(Orientation.VERTICAL, self.vertical_csv_path)

    def test_read_csv_horizontal(self):
        self.read_csv_and_test(Orientation.HORIZONTAL, self.horizontal_csv_path)


if __name__ == '__main__':
    unittest.main()
