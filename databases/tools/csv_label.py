from dataclasses import dataclass

from xrdpattern.crystal import Lengths, Angles


@dataclass
class CsvLabel:
    lengths : Lengths
    angles : Angles
    chemical_composition : str
    phase_fraction : float
    spacegroup : int
