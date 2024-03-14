from __future__ import annotations

from typing import Optional
import matplotlib.pyplot as plt
from dataclasses import dataclass
from hollarek.templates import JsonDataclass

from .intensity_map import IntensityMap, XAxisType
from .metadata import Metadata
import os
from uuid import uuid4
# -------------------------------------------

@dataclass
class XrdPattern(JsonDataclass):
    twotheta_to_intensity : dict[float, float]
    metadata: Metadata
    datafile_path : Optional[str] = None


    def plot(self, use_interpolation=True):
        if use_interpolation:
            std_mapping = self.get_data()
            angles = list(std_mapping.keys())
            intensities = list(std_mapping.values())
            label = 'Interpolated Intensity'
        else:
            angles = list(self.twotheta_to_intensity.keys())
            intensities = list(self.twotheta_to_intensity.values())
            label = 'Original Intensity'

        plt.figure(figsize=(10, 6))
        plt.plot(angles, intensities, label=label)
        plt.xlabel('Angle (Degrees)')
        plt.ylabel('Intensity')
        plt.title('XRD Pattern')
        plt.legend()
        plt.show()

    # -------------------------------------------
    # get

    def get_name(self) -> str:
        if self.datafile_path:
            file_name = os.path.basename(self.datafile_path)
            parts = file_name.split('.')
            if len(parts) == 2:
                file_name = parts[0]
        else:
            file_name = f'unnamed_file_{uuid4()}'
        return file_name


    def get_wavelength(self, primary : bool = True) -> float:
        wavelength_info = self.metadata.wavelength_info
        if primary:
            wavelength = wavelength_info.primary
        else:
            wavelength = wavelength_info.secondary
        if wavelength is None:
            raise ValueError(f"Wavelength is None")

        return wavelength


    def get_data(self, apply_standardization = True, x_axis_type : XAxisType = XAxisType.TwoTheta) -> IntensityMap:
        """
        :param apply_standardization: Standardization pads missing values, scales intensity into [0,1] range and makes x-step size uniform
        :param x_axis_type: Specifies the type of x-axis values, defaults to XAxisType.TwoTheta. This determines how the x-axis is interpreted and processed.
        :return: A mapping from the specified x-axis type to intensity
        """
        if x_axis_type == XAxisType.QValues:
            raise NotImplementedError

        mapping = IntensityMap(self.twotheta_to_intensity)
        if apply_standardization:
            start, stop, num_entries = 0, 90, 1000
            mapping = mapping.get_standardized(start_val=start, stop_val=stop, num_entries=num_entries)

        return IntensityMap(mapping)

    # -------------------------------------------

    def save(self, fpath : str):
        with open(fpath, 'w') as f:
            f.write(self.to_str())


