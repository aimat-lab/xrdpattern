from __future__ import annotations

from dataclasses import dataclass

from xrdpattern.powder.structure import CrystalStructure


# ---------------------------------------------------------

@dataclass
class Artifacts:
    primary_wavelength: float
    secondary_wavelength: float
    secondary_to_primary: float
    shape_factor : float = 0.9

    def as_list(self) -> list[float]:
        return [self.primary_wavelength, self.secondary_wavelength, self.secondary_to_primary, self.shape_factor]


@dataclass
class Powder:
    crystal_structure: CrystalStructure
    crystallite_size: float = 500
    temp_in_kelvin : int = 293

