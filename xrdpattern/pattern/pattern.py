from __future__ import annotations

import os
import time
from typing import Optional
from uuid import uuid4

import matplotlib.pyplot as plt
import torch
from CrystalStructure.crystal import CrystalStructure

# from holytools.fsys import SaveManager
from xrdpattern.core import PatternData, Artifacts
# from xrdpattern.parsing import Formats
from .pattern_report import PatternReport

# parser = Parser()
# -------------------------------------------

class XrdPattern(PatternData):
    def plot(self, title: str ='Xrd Pattern', save_fpath : Optional[str] = None, apply_standardization=True):
        plt.figure(figsize=(10, 6))
        plt.ylabel('Intensity')
        plt.title(title)

        x_values, intensities = self.get_pattern_data(apply_standardization=apply_standardization)
        if apply_standardization:
            label = 'Interpolated Intensity'
        else:
            label = 'Original Intensity'

        plt.xlabel(r'$2\theta$ (Degrees)')
        plt.plot(x_values, intensities, label=label)
        plt.legend()

        if save_fpath:
            plt.savefig(save_fpath)
            print(f"Plot saved to \"{save_fpath}\"")

        plt.show()

    # -------------------------------------------
    # save/load

    # @classmethod
    # def load(cls, fpath : str) -> XrdPattern:
    #     pattern_list = parser.extract(fpath=fpath)
    #     if len(pattern_list) > 1:
    #         raise ValueError('Multiple patterns found in file. Please use pattern database class instead')
    #     pattern_info = pattern_list[0]
    #
    #     kwargs = pattern_info.to_dict()
    #     return cls(**kwargs)

    @classmethod
    def load(cls, fpath : str) -> XrdPattern:
        with open(fpath, 'r') as file:
            data = file.read()
            new_pattern = PatternData.from_str(json_str=data)
        kwargs = new_pattern.to_dict()
        return cls(**kwargs)

    def save(self, fpath : str, force_overwrite : bool = False):
        # if not fpath.endswith(f'.{Formats.xrdpattern.suffix}'):
        #     fpath = SaveManager.ensure_suffix(fpath=fpath, suffix = Formats.xrdpattern.suffix)
        #     print(f'Fpath was automatically changed to \"{fpath}\" to comply with required suffix \"{Formats.xrdpattern.suffix}\"')
        if os.path.isfile(fpath) and not force_overwrite:
            raise ValueError(f'File {fpath} already exists')
        with open(fpath, 'w') as f:
            f.write(self.to_str())

    # -------------------------------------------
    # get

    @property
    def crystal_structure(self) -> CrystalStructure:
        return self.label.crystal_structure

    @property
    def powder(self):
        return self.label.powder

    @property
    def artifacts(self) -> Artifacts:
        return self.label.artifacts

    @property
    def is_simulated(self) -> bool:
        return self.label.is_simulated

    def to_tensor_pair(self) -> tuple[torch.Tensor, torch.Tensor]:
        now = time.time()

        labels = self.label.to_tensor()
        _, intensities = self.get_pattern_data()
        intensities = torch.tensor(intensities)

        time_taken = time.time() - now
        print(f'Time taken = {time_taken}')

        return intensities, labels

    def get_parsing_report(self, datafile_fpath : str) -> PatternReport:
        pattern_health = PatternReport(datafile_fpath=datafile_fpath)
        if len(self.two_theta_values) == 0:
            pattern_health.add_critical('No data found. Degree over intensity is empty!')
        elif len(self.two_theta_values) < 10:
            pattern_health.add_critical('Data is too short. Less than 10 entries!')

        if self.label.primary_wavelength is None:
            pattern_health.add_error('Primary wavelength missing!')
        if self.label.secondary_wavelength is None:
            pattern_health.add_warning('No secondary wavelength found')

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


    def get_pattern_data(self, apply_standardization = True) -> tuple[list[float], list[float]]:
        """
        :param apply_standardization: Standardization pads missing values, scales intensity into [0,1] range and makes x-step size uniform
        :return: A mapping from the specified x-axis type to intensity
        """

        if apply_standardization:
            start, stop = self.std_two_theta_range()
            num_entries = self.std_num_entries()
            intensity_map = self.get_standardized_map(start_val=start, stop_val=stop, num_entries=num_entries)
        else:
            intensity_map = (self.two_theta_values, self.intensities)
        return intensity_map

    @classmethod
    def std_num_entries(cls) -> int:
        return 2048

    @classmethod
    def std_two_theta_range(cls) -> (float, float):
        return 0, 90

    def get_info_as_str(self) -> str:
        crystal = self.label.crystal_structure
        pattern_content = str(self.intensities)[:50] + '...'
        try:
            crystal_data = str(crystal.to_pymatgen())
        except:
            crystal_data = 'No crystal data available'

        as_str = (f'----> Sample \n'
              f'- Crystal: {crystal_data} \n'
              f'- Metadata:\n'
              f'    - Crystallite size: {self.label.crystallite_size}\n'
              f'    - Temperature : {self.label.temp_in_celcius}\n'
              f'- Pattern:\n'
                  f'content: {pattern_content}\n'
                  f'length: {len(self.intensities)}\n')
        return as_str

    def __str__(self):
        return self.get_info_as_str()