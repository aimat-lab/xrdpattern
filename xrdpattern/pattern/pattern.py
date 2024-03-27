from __future__ import annotations

from typing import Optional
import matplotlib.pyplot as plt
from dataclasses import dataclass
import os
from uuid import uuid4

from hollarek.abstract import JsonDataclass
from .intensity_map import IntensityMap, XAxisType
from .metadata import Metadata
from .pattern_report import PatternReport
# -------------------------------------------

@dataclass
class XrdPattern(JsonDataclass):
    twotheta_to_intensity : dict[float, float]
    metadata: Metadata
    datafile_path : Optional[str] = None

    def plot(self, apply_standardization=True):
        plt.figure(figsize=(10, 6))
        plt.ylabel('Intensity')
        plt.title('XRD Pattern')

        intensity_map = self.get_data(apply_standardization=apply_standardization)
        x_values, intensities = intensity_map.as_list_pair()
        if apply_standardization:
            label = 'Interpolated Intensity'
        else:
            label = 'Original Intensity'

        if intensity_map.x_axis_type == XAxisType.TwoTheta:
            plt.xlabel(r'$2\theta$ (Degrees)')
        else:
            plt.xlabel(r'Q ($\AA^{-1}$)')

        plt.plot(x_values, intensities, label=label)
        plt.legend()
        plt.show()

    # -------------------------------------------
    # get

    def get_parsing_report(self) -> PatternReport:
        pattern_health = PatternReport(data_file_path=self.datafile_path)

        if len(self.twotheta_to_intensity) == 0:
            pattern_health.add_critical('No data found. Degree over intensity is empty!')
        elif len(self.twotheta_to_intensity) < 10:
            pattern_health.add_critical('Data is too short. Less than 10 entries!')
        if self.get_wavelength(primary=True) is None:
            pattern_health.add_error('Primary wavelength missing!')

        if self.get_wavelength(primary=False) is None:
            pattern_health.add_warning('No secondary wavelength found')
        if self.metadata.anode_material is None:
            pattern_health.add_warning('No anode material found')
        if self.metadata.measurement_date is None:
            pattern_health.add_warning('No measurement datetime found')

        return pattern_health


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

    def set_wavelength(self, new_wavelength : float, primary : bool = True):
        wavelength_info = self.metadata.wavelength_info
        if primary:
            wavelength_info.primary = new_wavelength
        else:
            wavelength_info.secondary = new_wavelength


    def get_data(self, apply_standardization = True, x_axis_type : XAxisType = XAxisType.TwoTheta) -> IntensityMap:
        """
        :param apply_standardization: Standardization pads missing values, scales intensity into [0,1] range and makes x-step size uniform
        :param x_axis_type: Specifies the type of x-axis values, defaults to XAxisType.TwoTheta. This determines how the x-axis is interpreted and processed.
        :return: A mapping from the specified x-axis type to intensity
        """
        if x_axis_type == XAxisType.QValues:
            raise NotImplementedError

        intensity_map = IntensityMap(self.twotheta_to_intensity,x_axis_type=XAxisType.TwoTheta)
        if apply_standardization:
            start, stop, num_entries = 0, 90, 1000
            intensity_map = intensity_map.get_standardized(start_val=start, stop_val=stop, num_entries=num_entries)

        return intensity_map

    # -------------------------------------------

    def save(self, fpath : str):
        with open(fpath, 'w') as f:
            f.write(self.to_str())


