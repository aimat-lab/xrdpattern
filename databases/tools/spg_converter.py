import re


to_int_dict = {}

with open('spg_formulas.txt', 'r') as f:
    content = f.read()
    rows = content.split('\n')

for r in [r for r in rows if len(r) > 0]:
    entries = re.split('[\t ]+', r)
    i = int(entries[0])
    for s in entries[1:]:
            to_int_dict[s] = i

def to_int(spg_formula : str) -> int:
    spg_formula = spg_formula.replace('-', '')
    spg_formula = spg_formula.replace('_', '')

    return to_int_dict[spg_formula]


print(to_int(spg_formula='Ia-3'))
