import os

from xrdpattern.core import CrystalStructure
from holytools.devtools import Unittest
from tests.locations import LocationManager

class TestPymatgenSpacegroup(Unittest):
    def test_spacegroup_calculation(self):
        if not LocationManager.root_exists():
            self.skipTest(reason="Root directory not set")

        cif_dirpath = LocationManager.cif_dirpath()
        cif_files = os.listdir(cif_dirpath)
        correct_count = 0
        total_count = 0

        for i, cif_file in enumerate(cif_files):
            if total_count >= 1000:
                break
            fpath = os.path.join(cif_dirpath, cif_file)
            try:
                structure = CrystalStructure.from_file(fpath=fpath)
                structure.calculate_properties()
                computed_sg = structure.space_group
                print(f'Computed space group = {computed_sg}')
                original_sg = self.parse_space_group_from_cif(fpath)

                if computed_sg == original_sg:
                    correct_count += 1
                    print(f'++ Correct spacegroup match for {cif_file}')
                else:
                    print(f'-- Incorrect spacegroup match for {cif_file}')
                total_count += 1
            except Exception as e:
                print(f"Error processing {cif_file}: {e}")

        print(f"Correct spacegroup matches: {correct_count}/{total_count} ({correct_count / total_count * 100:.2f}%)")
        self.assertTrue(correct_count / total_count > 0.95, "Less than 99% of spacegroups were correctly calculated")


    @staticmethod
    def parse_space_group_from_cif(fpath):
        with open(fpath,'r') as f:
            lines = f.readlines()

        spg = None
        for line in lines:
            if '_space_group_IT_number' in line:
                _, spg = line.split()
                spg = int(spg)
        print(f'Parsed spg number = {spg}')
        return spg



if __name__ == "__main__":
    TestPymatgenSpacegroup.execute_all()