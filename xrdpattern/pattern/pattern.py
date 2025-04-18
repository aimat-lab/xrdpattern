from __future__ import annotations

import copy
import os
from dataclasses import fields
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import CubicSpline

from xrdpattern.parsing import MasterParser, Formats
from xrdpattern.xrd import XrdData
from xrdpattern.xrd.experiment import PowderExperiment

parser = MasterParser()

# -------------------------------------------

class XrdPattern(XrdData):
    @classmethod
    def load(cls, fpath : str, mute : bool = False) -> XrdPattern:
        pattern_list = parser.extract(fpath=fpath)
        if len(pattern_list) > 1:
            raise ValueError('Multiple patterns found in file. Please use PatternDB class instead')
        pattern_info = pattern_list[0]
        kwargs = pattern_info.to_init_dict()
        pattern = cls(**kwargs)
        return pattern

    def save(self, fpath : str, force_overwrite : bool = False):
        if os.path.isfile(fpath) and not force_overwrite:
            raise ValueError(f'File {fpath} already exists')
        if not fpath.endswith(f'.{Formats.aimat_suffix()}'):
            print(f'[Warning]: Saved xrd files should end with ".{Formats.aimat_suffix()}" suffix. '
                  f'Given filename is {os.path.basename(fpath)}')
        with open(fpath, 'w') as f:
            f.write(self.to_str())

    # ------------------------------------------
    # standardization

    def get_pattern_data(self, apply_standardization : bool = True, num_entries : Optional[int] = None) -> tuple[NDArray, NDArray]:
        if not apply_standardization and not num_entries is None:
            raise ValueError('num_entries specifies target number entries for standardization. '
                             'Cannot be used without standardization')

        if apply_standardization:
            if num_entries is None:
                num_entries = self.std_num_entries()
            start, stop = self.std_two_theta_range()
            angles, intensities = self._get_uniform(start_val=start, stop_val=stop, num_entries=num_entries)
        else:
            angles, intensities = copy.deepcopy(self.two_theta_values), copy.copy(self.intensities)

        return angles, intensities

    def _get_uniform(self, start_val : float, stop_val : float, num_entries : int, constant_padding : bool = False) -> (list[float], list[float]):
        start, end = self.two_theta_values[0], self.two_theta_values[-1]
        std_angles = np.linspace(start=start_val, stop=stop_val, num=num_entries)

        x = np.array(self.two_theta_values)
        y = np.array(self.intensities)
        x, y = self.to_strictly_increasing(x, y)

        cs = CubicSpline(x, y)
        std_intensities = cs(std_angles)
        below_start_indices = np.where(std_angles < start)[0]
        above_end_indices = np.where(std_angles > end)[0]

        indices_in_range = np.where((std_angles >= start) & (std_angles <= end))[0]
        range_min = np.min(std_intensities[indices_in_range])
        std_intensities -= range_min

        if constant_padding:
            below_start, after_end = y[0], y[-1]
        else:
            below_start, after_end = 0, 0

        std_intensities[below_start_indices] = below_start
        std_intensities[above_end_indices] = after_end

        max_intensity = np.max(std_intensities)
        normalization_factor = max_intensity if max_intensity > 0 else 1
        std_intensities = std_intensities/normalization_factor

        return std_angles, std_intensities

    @staticmethod
    def to_strictly_increasing(x : NDArray, y : NDArray):
        indices = np.argsort(x)
        x_sorted, y_sorted = x[indices], y[indices]
        _, unique_indices = np.unique(x_sorted, return_index=True)
        x = x_sorted[unique_indices]
        y = y_sorted[unique_indices]

        return x, y

    def __eq__(self, other : XrdPattern):
        for attr in fields(self):
            v1, v2 = getattr(self, attr.name), getattr(other, attr.name)
            if isinstance(v1, np.ndarray):
                is_ok = np.array_equal(v1, v2)
            elif isinstance(v1, PowderExperiment):
                is_ok = v1
            else:
                is_ok = v1 == v2

            if not is_ok:
                return False
        return True

    # -------------------------------------------
    # display

    def plot(self, title: Optional[str] = None, save_fpath : Optional[str] = None, apply_standardization : bool =True):
        title = title or 'XrdPattern'

        x_values, intensities = self.get_pattern_data(apply_standardization=apply_standardization)
        quantity_qualifer = 'Relative' if apply_standardization else 'Original'
        quantity = 'intensitites'
        label = f'{quantity_qualifer} {quantity}'

        plt.figure(figsize=(10, 6))
        plt.title(title)
        plt.ylabel(f'{label}')
        plt.xlim(self.std_two_theta_range())
        plt.xlabel(r'$2\theta$ [$^\circ$]')
        plt.plot(x_values, intensities, label=label)
        plt.legend()

        if save_fpath:
            plt.savefig(save_fpath)
            print(f"Plot saved to \"{save_fpath}\"")

        plt.show()

    def get_info_as_str(self) -> str:
        crystal = self.primary_phase
        pattern_content = str(self.intensities)[:50] + '...'
        try:
            crystal_data = str(crystal.to_pymatgen())
        except:
            crystal_data = 'No components data available'

        as_str = (f'----> Sample \n'
              f'- Crystal: {crystal_data} \n'
              f'- Experiment Parameters:\n'
              f'    - Primary wavelength: {self.powder_experiment.xray_info.primary_wavelength}\n'
              f'    - Temperature : {self.powder_experiment.temp_K}\n'
              f'- Origin Metadata:\n'
                f'    - Contributor: {self.metadata.contributor_name}\n'
                f'    - Institution: {self.metadata.institution}\n'
              f'- Pattern:\n'
                  f'content: {pattern_content}\n'
                  f'length: {len(self.intensities)}\n')
        return as_str

    def __str__(self):
        return self.get_info_as_str()

    @classmethod
    def std_num_entries(cls) -> int:
        return 8192

    @classmethod
    def std_two_theta_range(cls) -> (float, float):
        return 0, 180