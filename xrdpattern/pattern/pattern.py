from __future__ import annotations

import matplotlib.pyplot as plt
import os
from uuid import uuid4

from xrdpattern.parsing import Parser, ParserOptions
from ..core import IntensityMap, XAxisType, PatternInfo
from .pattern_report import PatternReport
# -------------------------------------------

class XrdPattern(PatternInfo):
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

    @classmethod
    def load(cls, fpath : str, parser_options : ParserOptions = ParserOptions()):
        parser = Parser(parser_options=parser_options)
        pattern_list = parser.get_pattern_info_list(fpath=fpath)
        if len(pattern_list) > 1:
            raise ValueError('Multiple patterns found in file. Please use pattern database class instead')
        pattern = pattern_list[0]
        return cls(intensity_map=pattern.intensity_map, metadata=pattern.metadata, datafile_path=fpath)


    def save(self, fpath : str):
        with open(fpath, 'w') as f:
            f.write(self.to_str())

    # -------------------------------------------
    # get

    def get_parsing_report(self) -> PatternReport:
        pattern_health = PatternReport(data_file_path=self.datafile_path)

        if len(self.intensity_map.data) == 0:
            pattern_health.add_critical('No data found. Degree over intensity is empty!')
        elif len(self.intensity_map.data) < 10:
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


    def get_data(self, apply_standardization = True, x_axis_type : XAxisType = XAxisType.TwoTheta) -> IntensityMap:
        """
        :param apply_standardization: Standardization pads missing values, scales intensity into [0,1] range and makes x-step size uniform
        :param x_axis_type: Specifies the type of x-axis values, defaults to XAxisType.TwoTheta. This determines how the x-axis is interpreted and processed.
        :return: A mapping from the specified x-axis type to intensity
        """
        if x_axis_type == XAxisType.QValues:
            raise NotImplementedError

        intensity_map = self.intensity_map
        if apply_standardization:
            start, stop, num_entries = 0, 90, 1000
            intensity_map = intensity_map.get_standardized(start_val=start, stop_val=stop, num_entries=num_entries)

        print(f'intensity map in get data')
        return intensity_map


    def __eq__(self, other):
        if not isinstance(other, XrdPattern):
            return False
        return self.intensity_map == other.intensity_map and self.metadata == other.metadata
