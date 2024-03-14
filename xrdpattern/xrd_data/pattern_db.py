# from __future__ import annotations
#
# import shutil
# import os.path
# import os
# from uuid import uuid4
# from typing import Optional
# from dataclasses import dataclass
# from hollarek.io import FsysNode
# from xrdpattern.logging.logger import log_xrd_info
#
# from .pattern import XrdPattern
# # -------------------------------------------
#
#
# @dataclass
# class XrdPatternDB:
#     patterns : list[XrdPattern]
#
#     # def __init__(self, data_root_path : str,selected_formats : Optional[list[str]] = None):
#     #     self.root_path : str = data_root_path
#     #     self.selected_formats : Optional[list[str]] = selected_formats
#
#
#     def save(self, path : str):
#         is_occupied = os.path.isdir(path) or os.path.isfile(path)
#         if is_occupied:
#             raise ValueError(f'Path \"{path}\" is occupied by file/dir')
#         os.makedirs(path, exist_ok=True)
#
#         for pattern in self.patterns:
#             if pattern.datafile_path:
#                 file_name = os.path.basename(pattern.datafile_path)
#             if len(file_name.split('.')) == 2:
#                 file_name = file_name.split('.')[0] + '.json'
#             fpath = os.path.join(path, file_name)
#
#             pattern.save(fpath=fpath)
#         self.create_report(fpath=os.path.join(path, 'log.txt'))
#
#
#     def create_report(self, fpath : str):
#         def log(msg: str):
#             log_xrd_info(msg=msg, log_file_path=fpath)
#
#         num_unsuccessful = self.total_count-len(self.patterns)
#         summary_str =(f'\n----- Finished creating database -----'
#                       f'\n{num_unsuccessful}/{self.total_count} patterns could not be parsed')
#
#
#         num_crit, num_err, num_warn = 0,0,0
#         reports = [pattern.processing_report for pattern in self.patterns]
#         for report in reports:
#             num_crit += report.has_critical_error()
#             num_err += report.has_error()
#             num_warn += report.has_warning()
#
#         summary_str += f'\n{num_crit}/{self.total_count} patterns had critical error(s)'
#         summary_str += f'\n{num_err}/{self.total_count}  patterns had error(s)'
#         summary_str += f'\n{num_warn}/{self.total_count}  patterns had warning(s)'
#         log(f'{summary_str}\n\n'
#             f'----------------------------------------\n')
#
#         log(f'Individual file reports\n\n')
#         for pattern in self.patterns:
#             log(msg=str(pattern.processing_report))
#
#
#
#
#
#
#
#
# def find_free_path(dirpath: str, basename: str):
#     while True:
#         smol_uuid4 = str(uuid4())[:5]
#         fpath = f'{smol_uuid4}_{basename}'
#         if not fpath in os.listdir(path=dirpath):
#             return fpath
