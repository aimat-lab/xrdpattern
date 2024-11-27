from dataclasses import dataclass

from xrdpattern.crystal import Lengths, Angles, CrystalPhase


@dataclass
class CsvLabel:
    lengths : Lengths
    angles : Angles
    chemical_composition : str
    phase_fraction : float
    spacegroup : int

    def set_phase_properties(self, phase : CrystalPhase):
        phase.spacegroup = self.spacegroup
        phase.lengths = self.lengths
        phase.angles = self.angles
        phase.chemical_composition = self.chemical_composition
        phase.phase_fraction = self.phase_fraction
