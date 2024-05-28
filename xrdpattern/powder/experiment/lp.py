# from __future__ import annotations
#
# from dataclasses import dataclass
#
# from pymatgen.analysis.diffraction.core import DiffractionPattern
#
# from xrdpattern.pattern import XrdPattern
# from holytools.abstract import Dillable
# from .experiment import PowderExperiment
# # ---------------------------------------------------------
#
#
# @dataclass
# class LabeledPattern(Dillable):
#     pattern : XrdPattern
#     powder_experiment : PowderExperiment
#
#     def __post_init__(self):
#         if isinstance(self.pattern, XrdPattern):
#             data = self.pattern.get_data(apply_standardization=True)
#             _, values = data.as_list_pair()
#             return Tensor(values)
#
#         target_size = XrdPattern.get_std_num_entries()
#         actual_size = self.pattern.size(0)
#         if not actual_size == target_size:
#             raise ValueError(f'Incorrect number of entries in intensities: {actual_size}. Expected: {target_size}')
#
#     @classmethod
#     def load(cls, fpath : str) -> LabeledPattern:
#         return super().load(fpath=fpath)
#
#     # ---------------------------------------------------------
#
#     def as_str(self) -> str:
#         crystal = self.powder_experiment.crystal_structure
#         pattern_content = str(self.pattern.tolist())[:50] + '...'
#         as_str = (f'----> Sample \n'
#               f'- Crystal: {crystal.to_pymatgen()}\n'
#               f'- Metadata:\n'
#               f'    - Crystallite size: {self.powder_experiment.crystallite_size}\n'
#               f'    - Temperature : {self.powder_experiment.temp_in_celcius}\n'
#               f'- Pattern:\n'
#                   f'content: {pattern_content}\n'
#                   f'length: {len(self.pattern)}\n')
#         return as_str
#
#
#     def view(self):
#         num_entries = XrdPattern.get_std_num_entries()
#         start, end = XrdPattern.get_std_range()
#         x_values = [start + (end - start) * i / num_entries for i in range(num_entries)]
#         y_values = self.pattern.tolist()
#
#         pattern = XrdPattern.from_angle_map(angles=x_values, intensities=y_values)
#         pattern.plot()
#
#         print(f'--- Labeled Pattern Information ---')
#         print(self.as_str())
#
#     def __str__(self):
#         return self.as_str()
