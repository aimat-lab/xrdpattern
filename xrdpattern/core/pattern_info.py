from hollarek.abstract import JsonDataclass
from dataclasses import dataclass
from typing import Optional
from .xrd_intensities import XrdIntensities
from .metadata import Metadata


@dataclass
class PatternInfo(JsonDataclass):
    xrd_intensities : XrdIntensities
    metadata: Metadata
    datafile_path : Optional[str] = None


    def get_wavelength(self, primary : bool = True) -> Optional[float]:
        if primary:
            wavelength = self.metadata.primary
        else:
            wavelength = self.metadata.secondary
        if wavelength is None:
            raise ValueError(f"Wavelength is None")

        return wavelength


    def set_wavelength(self, new_wavelength : float, primary : bool = True):
        if primary:
            self.metadata.primary = new_wavelength
        else:
            self.metadata.secondary = new_wavelength