from __future__ import annotations

import copy
import os
from typing import Optional
from uuid import uuid4

import matplotlib.pyplot as plt
import numpy as np
import torch

from CrystalStructure.crystal import CrystalStructure
from numpy._typing import NDArray

# from holytools.fsys import SaveManager
from xrdpattern.core import PatternData, Artifacts
# from xrdpattern.parsing import Formats
from .pattern_report import PatternReport


# TODO: This is the correct loading mechanism but currently disabled due to incompatibbility of xylib with horeka
# parser = Parser()
# -------------------------------------------

class XrdPattern(PatternData):
    def plot(self, title: Optional[str] = None, save_fpath : Optional[str] = None,
             apply_standardization : bool =True,
             apply_autocorrelation : bool = False):
        title = title or self.name or 'XrdPattern'

        x_values, intensities = self.get_pattern_data(apply_standardization=apply_standardization, apply_autocorrelation=apply_autocorrelation)
        quantity_qualifer = 'Relative' if apply_standardization else 'Original'
        quantity = 'autocorrelated intensities' if apply_autocorrelation else 'intensitites'
        label = f'{quantity_qualifer} {quantity}'

        plt.figure(figsize=(10, 6))
        plt.title(title)
        plt.ylabel(f'{label}')
        plt.xlabel(r'$2\theta$ [°]')
        plt.plot(x_values, intensities, label=label)
        plt.legend()

        if save_fpath:
            plt.savefig(save_fpath)
            print(f"Plot saved to \"{save_fpath}\"")

        plt.show()

    @classmethod
    def mk_zero_intensities(cls) -> XrdPattern:
        start, stop = cls.std_two_theta_range()
        two_theta_values = np.linspace(start=start, stop=stop, num=cls.std_num_entries()).tolist()
        intensities = np.zeros(shape=(len(two_theta_values),)).tolist()
        return cls.make_unlabeled(two_theta_values=two_theta_values, intensities=intensities)


    # -------------------------------------------
    # save/load

    # TODO: This is the correct loading mechanism but currently disabled due to incompatibbility of xylib with horeka
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
    def startval(self):
        return self.two_theta_values[0]

    @property
    def endval(self):
        return self.two_theta_values[-1]

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

    def to_tensor_pair(self, dtype : torch.dtype, device : torch.device) -> tuple[torch.Tensor, torch.Tensor]:
        # now = time.time()

        labels = self.label.to_tensor(dtype=dtype, device=device)
        _, intensities = self.get_pattern_data()
        intensities = torch.tensor(intensities, dtype=dtype, device=device)

        # print(f'Time taken = {time.time() - now} seconds')

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


    def get_pattern_data(self, apply_standardization : bool = True, apply_autocorrelation : bool = False) -> tuple[NDArray, NDArray]:
        if apply_standardization:
            start, stop = self.std_two_theta_range()
            num_entries = self.std_num_entries()
            angles, intensities = self.get_standardized_map(start_val=start, stop_val=stop, num_entries=num_entries)
        else:
            angles, intensities = copy.deepcopy(self.two_theta_values), copy.copy(self.intensities)
        if apply_autocorrelation:
            intensities = intensities-np.sum(intensities)/len(intensities)
            intensities = np.correlate(intensities, intensities, mode='full')
            intensities -= np.min(intensities)

            max_intensity = np.max(intensities)
            normalization_factor = max_intensity if max_intensity > 0 else 1
            intensities = intensities / normalization_factor

            angles = np.linspace(0, 2 * angles[-1], len(intensities))
        return angles, intensities

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