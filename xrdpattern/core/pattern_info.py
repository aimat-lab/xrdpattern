from hollarek.abstract import JsonDataclass
from dataclasses import dataclass
from typing import Optional
from .xrd_data import XrdData
from .metadata import Metadata


@dataclass
class PatternInfo(JsonDataclass):
    xrd_data : XrdData
    metadata: Metadata
    datafile_path : Optional[str] = None


    def get_wavelength(self, primary : bool = True) -> float:
        wavelength_info = self.metadata.wavelength_info
        if primary:
            wavelength = wavelength_info.primary
        else:
            wavelength = wavelength_info.secondary
        if wavelength is None:
            raise ValueError(f"Wavelength is None")

        return wavelength


    def set_wavelength(self, new_wavelength : float, primary : bool = True):
        wavelength_info = self.metadata.wavelength_info
        if primary:
            wavelength_info.primary = new_wavelength
        else:
            wavelength_info.secondary = new_wavelength