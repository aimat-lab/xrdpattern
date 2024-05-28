import os
from xrdpattern.core import Labels, CrystalStructure, CrystalBase, Artifacts, PowderProperties

cif_fpath = os.path.join(os.path.dirname(__file__), "test.cif")
cif_fpath2 = os.path.join(os.path.dirname(__file__), 'test2.cif')

# ---------------------------------------------------------

class Examples:
    @staticmethod
    def get_sample():
        sample = PowderProperties(crystal_structure=Examples.get_crystal(mute=True), crystallite_size=500)
        artifact = Examples.get_artifacts()
        powder_sample = Labels(powder=sample, artifacts=artifact, is_simulated=True)
        return powder_sample

    @staticmethod
    def get_base(mute : bool = True) -> CrystalBase:
        crystal_stucture = Examples.get_crystal(mute=mute)
        return crystal_stucture.base


    @staticmethod
    def get_crystal(mute : bool = False):
        crystal_structure = CrystalStructure.from_cif(fpath=cif_fpath)
        if not mute:
            print(f'--> Cif content:\n {open(cif_fpath).read()}')
            print(f'--> Crystal structure:\n {crystal_structure}')
        return crystal_structure

    @staticmethod
    def get_artifacts() -> Artifacts:
        artifacts = Artifacts(primary_wavelength=1.54056, secondary_wavelength=1.54439, secondary_to_primary=0.5)
        return artifacts

    @staticmethod
    def get_cif_fpath(secondary : bool = False) -> str:
        return cif_fpath if not secondary else cif_fpath2



if __name__ == "__main__":
    the_sample = Examples.get_sample()
    the_sample.make_empty()
