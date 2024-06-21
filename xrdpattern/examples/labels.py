import os
from xrdpattern.core import PowderExperiment, CrystalStructure, CrystalBase, Artifacts, PowderSample

cif1_fpath = os.path.join(os.path.dirname(__file__), 'cifs', "test1.cif")
cif2_fpath = os.path.join(os.path.dirname(__file__), 'cifs', 'test2.cif')

# ---------------------------------------------------------

class LabelExamples:
    @staticmethod
    def get_label() -> PowderExperiment:
        sample = PowderSample(crystal_structure=LabelExamples.get_crystal(mute=True), crystallite_size=500)
        artifact = LabelExamples.get_artifacts()
        powder_sample = PowderExperiment(powder=sample, artifacts=artifact, is_simulated=True)
        return powder_sample

    @staticmethod
    def get_base(mute : bool = True) -> CrystalBase:
        crystal_stucture = LabelExamples.get_crystal(mute=mute)
        return crystal_stucture.base

    @staticmethod
    def get_crystal(mute : bool = False):
        cif_content = LabelExamples.get_cif_content()
        crystal_structure = CrystalStructure.from_cif(cif_content=cif_content)
        if not mute:
            print(f'--> Cif content:\n {open(cif1_fpath).read()}')
            print(f'--> Crystal structure:\n {crystal_structure}')
        return crystal_structure

    @staticmethod
    def get_artifacts() -> Artifacts:
        artifacts = Artifacts(primary_wavelength=1.54056, secondary_wavelength=1.54439, secondary_to_primary=0.5)
        return artifacts


    @staticmethod
    def get_cif_content(secondary : bool = False) -> str:
        cif_fpath = cif1_fpath if not secondary else cif2_fpath
        with open(cif_fpath, 'r') as f:
            cif_content = f.read()
        return cif_content


if __name__ == "__main__":
    the_sample = LabelExamples.get_label()
    the_sample.make_empty()
