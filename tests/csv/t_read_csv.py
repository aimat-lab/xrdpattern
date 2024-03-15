import unittest
from xrdpattern.parsing.csv import CsvPreprocessor, Orientation, TextTable, TableSelector
from hollarek.devtools import Unittest

class TestCsvPreprocessor(Unittest):

    def setUp(self):
        # Setup CsvPreprocessor with comma as a separator
        self.preprocessor = CsvPreprocessor(',')
        self.vertical_csv_path = 'vertical.csv'
        self.horizontal_csv_path = 'horizontal.csv'

    def test_read_csv_vertical(self):
        # Read vertically oriented CSV and validate the structure or content
        numerical_table = self.preprocessor.read_csv(self.vertical_csv_path, Orientation.VERTICAL)
        # self.assertIsInstance(numerical_table, type(expected_table))  # Check type
        # self.assertEqual(numerical_table, expected_table)  # Check content

    def test_read_csv_horizontal(self):
        numerical_table = self.preprocessor.read_csv(self.horizontal_csv_path, Orientation.HORIZONTAL)

if __name__ == '__main__':
    unittest.main()
