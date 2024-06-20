import os
from xrdpattern.core import Label, CrystalStructure, CrystalBase, ExperimentalArtifacts, PowderSample

cif_fpath = os.path.join(os.path.dirname(__file__), 'cifs', "test1.cif")
cif_fpath2 = os.path.join(os.path.dirname(__file__), 'cifs', 'test2.cif')

# ---------------------------------------------------------

class LabelExamples:
    @staticmethod
    def get_label() -> Label:
        sample = PowderSample(crystal_structure=LabelExamples.get_crystal(mute=True), crystallite_size=500)
        artifact = LabelExamples.get_artifacts()
        powder_sample = Label(powder=sample, artifacts=artifact, is_simulated=True)
        return powder_sample

    @staticmethod
    def get_base(mute : bool = True) -> CrystalBase:
        crystal_stucture = LabelExamples.get_crystal(mute=mute)
        return crystal_stucture.base


    @staticmethod
    def get_crystal(mute : bool = False):
        crystal_structure = CrystalStructure.from_file(fpath=cif_fpath)
        if not mute:
            print(f'--> Cif content:\n {open(cif_fpath).read()}')
            print(f'--> Crystal structure:\n {crystal_structure}')
        return crystal_structure

    @staticmethod
    def get_artifacts() -> ExperimentalArtifacts:
        artifacts = ExperimentalArtifacts(primary_wavelength=1.54056, secondary_wavelength=1.54439, secondary_to_primary=0.5)
        return artifacts

    @staticmethod
    def get_cif_fpath(secondary : bool = False) -> str:
        return cif_fpath if not secondary else cif_fpath2



if __name__ == "__main__":
    the_sample = LabelExamples.get_label()
    the_sample.make_empty()
