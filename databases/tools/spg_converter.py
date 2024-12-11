import os.path

from pymatgen.symmetry.groups import SpaceGroup


def get_formula_to_int(fpath):
    sg_dict = {}
    with open(fpath, 'r') as file:
        content = file.read()
        lines_with_eq = [l for l in content.split('\n') if '=' in l]
        for line in lines_with_eq:
            number_part, synonyms_part = line.split(' = ')
            number_part = number_part.replace(f'sg_synonyms[', '')
            number_part = number_part.replace(f']','')
            number = int(number_part)

            synonyms_part = synonyms_part.replace('\"', '')
            synonyms = synonyms_part.split('||')
            for s in synonyms:
                sg_dict[s] = number
    return sg_dict

dirpath = os.path.dirname(__file__)
rruff_formula_to_int = get_formula_to_int(fpath=os.path.join(dirpath, 'spg_formulas.txt'))


class SpacegroupConverter:
    @staticmethod
    def to_int(spg_formula : str) -> int:
        if spg_formula in rruff_formula_to_int:
            spg_int = rruff_formula_to_int[spg_formula]
        else:
            spg =  SpaceGroup(int_symbol=spg_formula)
            spg_int = spg.int_number
        return spg_int

    @staticmethod
    def to_formula(spg_int : int, mathmode : bool = False):
        sg = SpaceGroup.from_int_number(spg_int)
        symbol = sg.symbol
        if mathmode:
            symbol = symbol.replace(' ', '')
            symbol = symbol.replace('-', '\\text{-}')
        return symbol

    @staticmethod
    def get_all_formulas() -> list[str]:
        rruff_formulas = list(rruff_formula_to_int.keys())
        international_formula = [SpaceGroup.from_int_number(i).symbol for i in range(1, 231)]
        return rruff_formulas + international_formula

if __name__ == "__main__":
    # print(SpacegroupConverter.to_int(spg_formula='Ia-3'))
    print(f'formula to int dict = {rruff_formula_to_int}')
