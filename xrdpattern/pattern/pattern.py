from __future__ import annotations
import matplotlib.pyplot as plt
import os
from uuid import uuid4
from typing import Optional
from holytools.fsys import SaveManager
from dataclasses import asdict

from xrdpattern.parsing import Parser, ParserOptions
from xrdpattern.core import PatternInfo, Metadata
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

        plt.xlabel(r'$2\theta$ (Degrees)')

        plt.plot(x_values, intensities, label=label)
        plt.legend()
        plt.show()

    # -------------------------------------------

    @classmethod
    def load(cls, fpath : str, wavelength : Optional[float] = None) -> XrdPattern:
        options = ParserOptions(default_wavelength=wavelength)
        parser = Parser(parser_options=options)
        pattern_list = parser.get_pattern_info_list(fpath=fpath)
        if len(pattern_list) > 1:
            raise ValueError('Multiple patterns found in file. Please use pattern database class instead')
        pattern_info = pattern_list[0]


        kwargs = pattern_info.to_dict()
        return cls(**kwargs)


    def save(self, fpath : str, force_overwrite : bool = False):
        if not fpath.endswith(f'.json'):
            fpath = SaveManager.ensure_suffix(fpath, suffix = 'json')
        if os.path.isfile(fpath) and not force_overwrite:
            raise ValueError(f'File {fpath} already exists')
        with open(fpath, 'w') as f:
            f.write(self.to_str())

    @classmethod
    def from_intensitiy_map(cls, angles: list[float], intensities: list[float]) -> XrdPattern:
        metadata = Metadata.make_empty()
        return XrdPattern(two_theta_values=angles, intensities=intensities, metadata=metadata)

    # -------------------------------------------
    # get

    def get_parsing_report(self, datafile_fpath : str) -> PatternReport:
        pattern_health = PatternReport(datafile_fpath=datafile_fpath)
        if len(self.two_theta_values) == 0:
            pattern_health.add_critical('No data found. Degree over intensity is empty!')
        elif len(self.two_theta_values) < 10:
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


    def get_data(self, apply_standardization = True) -> (list[float], list[float]):
        """
        :param apply_standardization: Standardization pads missing values, scales intensity into [0,1] range and makes x-step size uniform
        :return: A mapping from the specified x-axis type to intensity
        """

        if apply_standardization:
            start, stop = self.get_std_range()
            num_entries = self.get_std_num_entries()
            intensity_map = self.get_standardized_map(start_val=start, stop_val=stop, num_entries=num_entries)
        else:
            intensity_map = (self.two_theta_values, self.intensities)
        return intensity_map

    @classmethod
    def get_std_num_entries(cls) -> int:
        return 2048

    @classmethod
    def get_std_range(cls) -> (float, float):
        return 0, 90


