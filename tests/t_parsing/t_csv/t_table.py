from xrdpattern.parsing.csv import TextTable, TableSelector
from holytools.devtools import Unittest

from xrdpattern.parsing.csv.tables import Region, Index


class TestTableSelector(Unittest):

    def setUp(self):
        self.table_3x3 = [
            ["1", "0", "0"],
            ["1", "1", "1"],
            ["0", "1", "1"]
        ]

        self.table_5x5 = [
            ["1", "1", "0", "0", "0"],
            ["1", "1", "1", "0x0", "0"],
            ["0", "1", "1", "1", "1"],
            ["0", "1", "1", "1", "1"],
            ["0", "1", "1", "1", "1"]
        ]

        self.example_table_data = [
            ['Name', 'Age', 'Score'],
            ['Alice', '30', '85.5'],
            ['Bob', '25.3', '92.0'],
            ['Charlie', '35', '88.3']
        ]

        self.test_discriminator = lambda x: x == '1'

    def test_3x3_table(self):
        table = TextTable(self.table_3x3)
        selector = TableSelector(table=table, discriminator=self.test_discriminator)
        expected_region = Region(Index(1, 1), Index(2, 2))
        self.assertEqual(selector.get_lower_right_region(), expected_region)

    def test_5x5_table(self):
        table = TextTable(self.table_5x5)
        selector = TableSelector(table=table, discriminator=self.test_discriminator)
        expected_region = Region(Index(2, 1), Index(4, 4))
        self.assertEqual(selector.get_lower_right_region(), expected_region)

    def test_example_table(self):
        table = TextTable(self.example_table_data)
        numerical_subtable = TableSelector.get_numerical_subtable(table=table)
        self.assertEqual(numerical_subtable.headers,['Age', 'Score'])
        self.assertIn([30,85.5], numerical_subtable.data)
        self.assertIn('Name', numerical_subtable.preable)



if __name__ == '__main__':
    TestTableSelector.execute_all()
