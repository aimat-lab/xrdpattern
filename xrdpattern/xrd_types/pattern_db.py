from __future__ import annotations

import os.path
import os
from uuid import uuid4

from hollarek.resources import FsysNode

from xrdpattern.xrd_file_io import FormatSelector
from xrdpattern.xrd_logger import log_xrd_info
from .pattern import XrdPattern
from typing import Optional

from ..xrd_file_io.formats import allowed_suffix_types


# -------------------------------------------


class XrdPatternDB:
    def __init__(self, log_file_path : Optional[str] = None):
        self.patterns : list[XrdPattern] = []
        self.log_file_path : Optional[str] = log_file_path
        self.num_unsuccessful : int = 0
        self.total_count : int = 0


    def import_data(self, dir_path : str, format_selector : FormatSelector = FormatSelector.make_allow_all()):
        if not os.path.isdir(dir_path):
            raise ValueError(f"Given path {dir_path} is not a directory")
        for file_path in find_xrd_files(dir_path=dir_path, format_selector=format_selector):
            try:
                new_pattern = XrdPattern(filepath=file_path)
                self.patterns.append(new_pattern)
            except Exception as e:
                self.num_unsuccessful += 1
                self.log(f"Could not import pattern from file {file_path}. Error: {str(e)}")
            finally:
                self.total_count += 1
        self.create_db_report()


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


    def log(self, msg : str):
        log_xrd_info(msg=msg, log_file_path=self.log_file_path)


    def create_db_report(self):
        summary_str = f'\n----- Finished creating database -----'
        summary_str += f'\n{self.num_unsuccessful}/{self.total_count} patterns could not be parsed'

        num_critical_patterns = len([pattern for pattern in self.patterns if pattern.processing_report.has_critical_error()])
        num_error_patterns = len([pattern for pattern in self.patterns if pattern.processing_report.has_error()])
        num_warning_patterns = len([pattern for pattern in self.patterns if pattern.processing_report.has_warning()])

        summary_str += f'\n{num_critical_patterns}/{self.total_count} patterns had critical error(s)'
        summary_str += f'\n{num_error_patterns}/{self.total_count}  patterns had error(s)'
        summary_str += f'\n{num_warning_patterns}/{self.total_count}  patterns had warning(s)'
        self.log(f'{summary_str}\n\n'
                 f'----------------------------------------\n')


        self.log(f'Individual file reports\n\n')
        for pattern in self.patterns:
            self.log(msg=str(pattern.processing_report))


def find_xrd_files(dir_path : str, format_selector : Optional[FormatSelector]) -> list[str]:
    if not os.path.isdir(dir_path):
        raise ValueError(f"Given path {dir_path} is not a directory")
    root_node = FsysNode(path=dir_path)
    xrd_files_nodes = root_node.select_file_nodes(allowed_formats=allowed_suffix_types)

    xrd_file_paths = [node.path for node in xrd_files_nodes if format_selector.is_allowed(node.get_suffix())]
    return xrd_file_paths
