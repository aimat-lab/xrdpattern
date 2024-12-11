import re

from pymatgen.symmetry.groups import SpaceGroup

to_int_dict = {}

with open('spg_formulas.txt', 'r') as f:
    content = f.read()
    rows = content.split('\n')

for r in [r for r in rows if len(r) > 0]:
    entries = re.split('[\t ]+', r)
    i = int(entries[0])
    for s in entries[1:]:
            to_int_dict[s] = i

class SpacegroupConverter:
    @staticmethod
    def to_int(spg_formula : str) -> int:
        spg_formula = spg_formula.replace('-', '')
        spg_formula = spg_formula.replace('_', '')

        return to_int_dict[spg_formula]

    @staticmethod
    def to_formula(spg_int : int):
        sg = SpaceGroup.from_int_number(spg_int)
        return sg.symbol


if __name__ == "__main__":
    print(SpacegroupConverter.to_int(spg_formula='Ia-3'))
