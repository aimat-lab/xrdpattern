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
print(selector.get_lower_right_subtable())