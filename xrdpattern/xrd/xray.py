from dataclasses import dataclass
from enum import Enum
from typing import Optional

from holytools.abstract import JsonDataclass


@dataclass
class XRayInfo(JsonDataclass):
    primary_wavelength: Optional[float]
    secondary_wavelength: Optional[float]

    @classmethod
    def mk_empty(cls):
        return cls(primary_wavelength=None, secondary_wavelength=None)

    def as_list(self) -> list[float]:
        return [self.primary_wavelength, self.secondary_wavelength]

    @staticmethod
    def default_ratio() -> float:
        return 0.5


class XrdAnode(Enum):
    Cu = "Cu"
    Mo = "Mo"
    Cr = "Cr"
    Fe = "Fe"
    Co = "Co"
    Ag = "Ag"

    def get_wavelengths(self) -> (float, float):
        MATERiAL_TO_WAVELENGTHS = {
            "Cu": (1.54439, 1.54056),
            "Mo": (0.71359, 0.70930),
            "Cr": (2.29361, 2.28970),
            "Fe": (1.93998, 1.93604),
            "Co": (1.79285, 1.78896),
            "Ag": (0.563813, 0.559421),
        }
        return MATERiAL_TO_WAVELENGTHS[self.value]



    def get_xray_info(self) -> XRayInfo:
        primary, secondary = self.get_wavelengths()
        return XRayInfo(primary_wavelength=primary, secondary_wavelength=secondary)