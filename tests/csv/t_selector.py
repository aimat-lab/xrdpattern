from xrdpattern.parsing.csv import TableSelector, TextTable

# 2x2 Table
table_2x2 = [
    ["1", "1"],
    ["1", "0"]
]

# 3x3 Table
table_3x3 = [
    ["1", "0", "0"],
    ["1", "1", "1"],
    ["0", "1", "1"]
]

table4x4 = [
    ["1", "1", "1", "0"],
    ["1", "1", "0", "0"],
    ["1", "0", "0", "0"],
    ["1", "1", "1", "1"]
]

# 5x5 Table
table_5x5 = [
    ["1", "1", "0", "0", "0"],
    ["1", "1", "1", "0", "0"],
    ["0", "1", "1", "1", "1"],
    ["0", "1", "1", "1", "1"],
    ["0", "1", "1", "1", "1"]
]

test_disc = lambda x: x == '1'
text_table = TextTable(table_5x5)
# text_table.get_maximal_region(test_disc)
selector = TableSelector(table=text_table, discriminator=test_disc)
# print(selector.get_lower_right_region())



example_table = TextTable([
    ['Name', 'Age', 'Score'],  # Textual header row
    ['Alice', '30', '85.5'],   # Mixed row: text and numerical data (as strings)
    ['Bob', '25', '92.0'],     # Mixed row: text and numerical data (as strings)
    ['Charlie', '35', '88.3']  # Mixed row: text and numerical data (as strings)
])

# Display the table's content to verify it's rectangular and mixed
numerical_subtable = TableSelector.get_numerical_subtable(table=example_table)
print(numerical_subtable)
print(f'done')