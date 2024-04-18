from __future__ import annotations
import matplotlib.pyplot as plt
import os
from uuid import uuid4
from typing import Optional
from hollarek.fsys import SaveManager

from xrdpattern.parsing import Parser, XrdFormat, ParserOptions
from xrdpattern.core import XrdIntensities, XAxisType, PatternInfo
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
    def load(cls, fpath : str, format_hint : Optional[XrdFormat] = None, wavelength : Optional[float] = None) -> XrdPattern:
        options = ParserOptions(default_format_hint=format_hint,default_wavelength_angstr=wavelength)
        parser = Parser(parser_options=options)
        pattern_list = parser.get_pattern_info_list(fpath=fpath)
        if len(pattern_list) > 1:
            raise ValueError('Multiple patterns found in file. Please use pattern database class instead')
        pattern_info = pattern_list[0]
        return cls(xrd_intensities=pattern_info.xrd_intensities, metadata=pattern_info.metadata, name=pattern_info.name)


    def save(self, fpath : str, force_overwrite : bool = False):
        if not fpath.endswith(f'.json'):
            fpath = SaveManager.ensure_suffix(fpath, suffix = 'json')
        if os.path.isfile(fpath) and not force_overwrite:
            raise ValueError(f'File {fpath} already exists')
        with open(fpath, 'w') as f:
            f.write(self.to_str())

    # -------------------------------------------
    # get

    def get_parsing_report(self, datafile_fpath : str) -> PatternReport:
        pattern_health = PatternReport(datafile_fpath=datafile_fpath)
        if len(self.xrd_intensities.data) == 0:
            pattern_health.add_critical('No data found. Degree over intensity is empty!')
        elif len(self.xrd_intensities.data) < 10:
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
        filename = self.name
        if filename:
            parts = self.name.split('.')
            if len(parts) == 2:
                filename = parts[0]
        else:
            filename = f'unnamed_file_{uuid4()}'
        return filename


    def get_data(self, apply_standardization = True, x_axis_type : XAxisType = XAxisType.TwoTheta) -> XrdIntensities:
        """
        :param apply_standardization: Standardization pads missing values, scales intensity into [0,1] range and makes x-step size uniform
        :param x_axis_type: Specifies the type of x-axis values, defaults to XAxisType.TwoTheta. This determines how the x-axis is interpreted and processed.
        :return: A mapping from the specified x-axis type to intensity
        """
        if x_axis_type == XAxisType.QValues:
            raise NotImplementedError

        intensity_map = self.xrd_intensities
        if apply_standardization:
            start, stop = self.get_std_range()
            num_entries = self.get_std_num_entries()
            intensity_map = intensity_map.get_standardized(start_val=start, stop_val=stop, num_entries=num_entries)
        return intensity_map

    @classmethod
    def get_std_num_entries(cls) -> int:
        return 2000

    @classmethod
    def get_std_range(cls) -> (float, float):
        return 0, 90

    def __eq__(self, other):
        if not isinstance(other, XrdPattern):
            return False
        return self.xrd_intensities == other.xrd_intensities and self.metadata == other.metadata

