import unittest
import os
from xrdpattern.parsing.csv import CsvPreprocessor, Orientation, TextTable, TableSelector
from hollarek.devtools import Unittest

class TestCsvPreprocessor(Unittest):

    def setUp(self):
        # Setup CsvPreprocessor with comma as a separator
        self.preprocessor = CsvPreprocessor(',')
        test_dirpath = os.path.dirname(os.path.abspath(__file__))
        self.vertical_csv_path = os.path.join(test_dirpath,'vertical.csv')
        self.horizontal_csv_path = os.path.join(test_dirpath,'horizontal.csv')
        self.first_row = [1.79272, 1.80218, 1.81164, 1.8211, 1.83056, 1.84002, 1.84948, 1.85894, 1.8684]

    def test_read_csv_vertical(self):
        numerical_table = self.preprocessor.read_csv(self.vertical_csv_path, Orientation.VERTICAL)
        expected_set = set(self.first_row)
        actual_set = set(numerical_table.data[0])
        self.assertTrue(expected_set.issubset(actual_set))

    def test_read_csv_horizontal(self):
        numerical_table = self.preprocessor.read_csv(self.horizontal_csv_path, Orientation.HORIZONTAL)
        expected_set = set(self.first_row)
        actual_set = set(numerical_table.data[0])
        self.assertTrue(expected_set.issubset(actual_set))


if __name__ == '__main__':
    unittest.main()
