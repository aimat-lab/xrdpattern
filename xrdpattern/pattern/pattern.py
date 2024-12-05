from __future__ import annotations

import copy
import os
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import torch
from numpy.typing import NDArray

from xrdpattern.parsing import MasterParser, Formats
from xrdpattern.xrd import XrdPatternData
from .pattern_report import ParsingReport

parser = MasterParser()

# -------------------------------------------

class XrdPattern(XrdPatternData):
    def plot(self, title: Optional[str] = None, save_fpath : Optional[str] = None, apply_standardization : bool =True):
        title = title or 'XrdPattern'

        x_values, intensities = self.get_pattern_data(apply_standardization=apply_standardization)
        quantity_qualifer = 'Relative' if apply_standardization else 'Original'
        quantity = 'intensitites'
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

    @classmethod
    def load(cls, fpath : str, mute : bool = False) -> XrdPattern:
        pattern_list = parser.extract(fpath=fpath)
        if len(pattern_list) > 1:
            raise ValueError('Multiple patterns found in file. Please use PatternDB class instead')
        pattern_info = pattern_list[0]
        kwargs = pattern_info.to_dict()
        pattern = cls(**kwargs)

        report = pattern.get_parsing_report(datafile_fpath=fpath)
        if not mute:
            print(report.as_str())
        return pattern

    def save(self, fpath : str, force_overwrite : bool = False):
        if os.path.isfile(fpath) and not force_overwrite:
            raise ValueError(f'File {fpath} already exists')
        if not fpath.endswith(f'.{Formats.aimat_suffix()}'):
            print(f'[Warning]: Saved xrd files should end with ".{Formats.aimat_suffix()}" suffix. '
                  f'Given filename is {os.path.basename(fpath)}')
        with open(fpath, 'w') as f:
            f.write(self.to_str())

    # -------------------------------------------
    # get

    def to_tensorpair(self, dtype : torch.dtype, device : torch.device) -> tuple[torch.Tensor, torch.Tensor]:
        raise NotImplementedError

        # now = time.time()
        # labels = self.label.to_tensor(dtype=dtype, device=device)
        # _, intensities = self.get_pattern_data()
        # intensities = torch.tensor(intensities, dtype=dtype, device=device)
        # print(f'Time taken = {time.time() - now} seconds')
        # return intensities, labels

    def get_parsing_report(self, datafile_fpath : str = 'Unmarked pattern') -> ParsingReport:
        pattern_health = ParsingReport(datafile_fpath=datafile_fpath)
        if self.powder_experiment.primary_wavelength is None:
            pattern_health.add_error('Primary wavelength missing!')
        return pattern_health

    def get_pattern_data(self, apply_standardization : bool = True, apply_constant_padding : bool = False,
                         zero_mask_below : float = 0,
                         zero_mask_above : float = 90) -> tuple[NDArray, NDArray]:
        if apply_standardization:
            start, stop = self.std_two_theta_range()
            num_entries = self.std_num_entries()
            angles, intensities = self._get_uniform(start_val=start, stop_val=stop, num_entries=num_entries, constant_padding=apply_constant_padding)
        else:
            angles, intensities = copy.deepcopy(self.two_theta_values), copy.copy(self.intensities)
        mask = (angles >= zero_mask_below) & (angles <= zero_mask_above)
        intensities = mask * intensities

        return angles, intensities

    @classmethod
    def std_num_entries(cls) -> int:
        return 8192

    @classmethod
    def std_two_theta_range(cls) -> (float, float):
        return 0, 90

    def get_info_as_str(self) -> str:
        crystal = self.powder_experiment.primary_phase
        pattern_content = str(self.intensities)[:50] + '...'
        try:
            crystal_data = str(crystal.to_pymatgen())
        except:
            crystal_data = 'No components data available'

        as_str = (f'----> Sample \n'
              f'- Crystal: {crystal_data} \n'
              f'- Experiment Parameters:\n'
              f'    - Primary wavelength: {self.xray_info.primary_wavelength}\n'
              f'    - Temperature : {self.powder_experiment.temp_in_celcius}\n'
              f'- Origin Metadata:\n'
                f'    - Contributor: {self.metadata.contributor_name}\n'
                f'    - Institution: {self.metadata.institution}\n'
              f'- Pattern:\n'
                  f'content: {pattern_content}\n'
                  f'length: {len(self.intensities)}\n')
        return as_str

    def __str__(self):
        return self.get_info_as_str()
