from holytools.devtools import Unittest
from xrdpattern.core import CrystalStructure
from xrdpattern.examples import LabelExamples


class TestPymatgenSpacegroup(Unittest):
    def setUp(self):
        with open(LabelExamples.get_cif_content(), 'r') as f:
            cif1 = f.read()
        with open(LabelExamples.get_cif_content(secondary=True), 'r') as f:
            cif2 = f.read()

        self.cifs : list[str] =  [cif1, cif2]

    def test_spacegroup_calculation(self):
        for cif in self.cifs:
            structure = CrystalStructure.from_cif(cif_content=cif)
            structure.calculate_properties()
            computed_sg = structure.space_group
            print(f'Computed space group = {computed_sg}')
            original_sg = self.extract_spg(cif)

            if computed_sg != original_sg:
                raise ValueError(f'Computed spg {computed_sg} does not match actual spg {original_sg} given in cif files')

    @staticmethod
    def extract_spg(cif : str) -> int:
        lines = cif.split('\n')
        spg = None
        for line in lines:
            if '_space_group_IT_number' in line:
                _, spg = line.split()
                spg = int(spg)
        print(f'Parsed spg number = {spg}')
        return spg



if __name__ == "__main__":
    TestPymatgenSpacegroup.execute_all()