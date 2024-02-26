from __future__ import annotations

import shutil
import os.path
import os
from uuid import uuid4
from typing import Optional

from hollarek.io import FsysNode
from xrdpattern.xrd_file_io import FormatSelector
from xrdpattern.xrd_logger import log_xrd_info

from .pattern import XrdPattern
from ..xrd_file_io.formats import allowed_suffix_types
# -------------------------------------------


class XrdPatternDB:
    def __init__(self, data_root_path : str, format_selector : FormatSelector = FormatSelector.make_allow_all()):
        self.patterns : list[XrdPattern] = []
        self.root_path : str = data_root_path

        self.format_selector : FormatSelector = format_selector
        self.num_unsuccessful : int = 0
        self.total_count : int = 0
        self.import_data()


    def import_data(self):
        if not os.path.isdir(self.root_path):
            raise ValueError(f"Given path {self.root_path} is not a directory")
        for filepath in find_xrd_files(dir_path=self.root_path, format_selector=self.format_selector):
            print(f'{filepath}')
            try:
                new_pattern = XrdPattern(filepath=filepath)
                self.patterns.append(new_pattern)
            except Exception as e:
                self.num_unsuccessful += 1
                print(f"Could not import pattern from file {filepath}. Error: {str(e)}")
            finally:
                self.total_count += 1


    def export_data(self, dir_path : dir):
        try:
            os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Could not create directory at {dir_path}. Error: {str(e)}")

        for pattern in self.patterns:
            file_name = os.path.basename(pattern.filepath)
            fpath = os.path.join(dir_path, file_name)

            if os.path.isfile(fpath):
                fpath = uuid4()
            pattern.export_data(filepath=fpath)
        self.create_db_report(dir_path=dir_path)


    def export_data_files(self, target_dir : str, allowed_formats : FormatSelector = FormatSelector.make_allow_all()):
        os.makedirs(target_dir, exist_ok=True)
        raw_data_paths = find_xrd_files(dir_path=self.root_path, format_selector=allowed_formats)

        for path in raw_data_paths:
            filename = find_free_path(dirpath=target_dir, basename=os.path.basename(path))
            fpath = os.path.join(target_dir, filename)
            shutil.copy(path, fpath)


    def create_db_report(self, dir_path : str):
        def log(msg: str):
            log_xrd_info(msg=msg, log_file_path=os.path.join(dir_path, 'log.txt'))

        summary_str = f'\n----- Finished creating database -----'
        summary_str += f'\n{self.num_unsuccessful}/{self.total_count} patterns could not be parsed'

        num_critical_patterns = len([pattern for pattern in self.patterns if pattern.processing_report.has_critical_error()])
        num_error_patterns = len([pattern for pattern in self.patterns if pattern.processing_report.has_error()])
        num_warning_patterns = len([pattern for pattern in self.patterns if pattern.processing_report.has_warning()])

        summary_str += f'\n{num_critical_patterns}/{self.total_count} patterns had critical error(s)'
        summary_str += f'\n{num_error_patterns}/{self.total_count}  patterns had error(s)'
        summary_str += f'\n{num_warning_patterns}/{self.total_count}  patterns had warning(s)'
        log(f'{summary_str}\n\n'
                 f'----------------------------------------\n')


        log(f'Individual file reports\n\n')
        for pattern in self.patterns:
            log(msg=str(pattern.processing_report))




def find_xrd_files(dir_path : str, format_selector : Optional[FormatSelector]) -> list[str]:
    if not os.path.isdir(dir_path):
        raise ValueError(f"Given path {dir_path} is not a directory")
    root_node = FsysNode(path=dir_path)
    xrd_files_nodes = root_node.select_file_subnodes(allowed_formats=allowed_suffix_types)

    xrd_file_paths = [node.get_path() for node in xrd_files_nodes if format_selector.is_allowed(node.get_suffix())]
    return xrd_file_paths


def find_free_path(dirpath: str, basename: str):
    while True:
        smol_uuid4 = str(uuid4())[:5]
        fpath = f'{smol_uuid4}_{basename}'
        if not fpath in os.listdir(path=dirpath):
            return fpath
