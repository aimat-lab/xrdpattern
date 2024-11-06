import os

from .components import CrystalStructure, CrystalBase

# ---------------------------------------------------------

class CrystalExamples:
    @staticmethod
    def get_crystal(num: int, verbose: bool = False):
        cif_content = CrystalExamples.get_cif_content(num=num)
        crystal_structure = CrystalStructure.from_cif(cif_content=cif_content)
        if verbose:
            print(f'--> Cif content:\n {cif_content}')
            print(f'--> Crystal structure:\n {crystal_structure}')
        return crystal_structure

    @staticmethod
    def get_base(num : int = 1, verbose : bool = False) -> CrystalBase:
        crystal_stucture = CrystalExamples.get_crystal(num=num, verbose=verbose)
        return crystal_stucture.base

    @staticmethod
    def get_cif_content(num : int = 1) -> str:
        cif_fpath = os.path.join(os.path.dirname(__file__), 'cifs', f"test{num}.cif")
        with open(cif_fpath, 'r') as f:
            cif_content = f.read()
        return cif_content
