from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from xrdpattern.serialization import JsonDataclass


@dataclass
class XrayInfo(JsonDataclass):
    primary_wavelength: Optional[float]
    secondary_wavelength: Optional[float]

    @classmethod
    def copper_xray(cls) -> XrayInfo:
        return cls.from_anode(element=XrdAnode.Cu)

    @classmethod
    def from_anode(cls, element : str):
        MATERIAL_TO_WAVELNGTHS = {
            "Cu": (1.54439, 1.54056),
            "Mo": (0.71359, 0.70930),
            "Cr": (2.29361, 2.28970),
            "Fe": (1.93998, 1.93604),
            "Co": (1.79285, 1.78896),
            "Ag": (0.563813, 0.559421),
        }
        return cls(*MATERIAL_TO_WAVELNGTHS[element])

    @classmethod
    def mk_empty(cls):
        return cls(primary_wavelength=None, secondary_wavelength=None)

    def as_list(self) -> list[float]:
        return [self.primary_wavelength, self.secondary_wavelength]

    @staticmethod
    def default_ratio() -> float:
        return 0.5


class XrdAnode:
    Cu : str = "Cu"
    Mo : str = "Mo"
    Cr : str = "Cr"
    Fe : str = "Fe"
    Co : str = "Co"
    Ag : str = "Ag"
