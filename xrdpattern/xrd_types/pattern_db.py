from __future__ import annotations

import shutil
import os.path
import os
from uuid import uuid4
from typing import Optional

from hollarek.io import FsysNode
from xrdpattern.xrd_logger import log_xrd_info
from xrdpattern.xrd_file_io.formats import allowed_suffixes

from .pattern import XrdPattern
# -------------------------------------------


class XrdPatternDB:
    def __init__(self, data_root_path : str,selected_formats : Optional[list[str]] = None):
        self.root_path : str = data_root_path
        self.selected_formats : Optional[list[str]] = selected_formats

        self.patterns : list[XrdPattern] = []
        self.total_count : int = 0
        self.import_data()


    def import_data(self):
        if not os.path.isdir(self.root_path):
            raise ValueError(f"Given path {self.root_path} is not a directory")
        data_fpaths = self.get_data_fpaths()
        self.total_count = len(data_fpaths)
        for filepath in data_fpaths:
            try:
                new_pattern = XrdPattern(filepath=filepath)
                self.patterns.append(new_pattern)
            except Exception as e:
                print(f"Could not import pattern from file {filepath}. Error: {str(e)}")


    def export(self, target_dir : str):
        try:
            os.makedirs(target_dir, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Could not create directory at {target_dir}. Error: {str(e)}")

        for pattern in self.patterns:
            file_name = os.path.basename(pattern.filepath)
            if len(file_name.split('.')) == 2:
                file_name = file_name.split('.')[0] + '.json'
            fpath = os.path.join(target_dir, file_name)

            if os.path.isfile(fpath):
                fpath = uuid4()
            pattern.export(filepath=fpath)
        self.create_report(dir_path=target_dir)


    def create_report(self, dir_path : str):
        def log(msg: str):
            log_xrd_info(msg=msg, log_file_path=os.path.join(dir_path, 'log.txt'))

        num_unsuccessful = self.total_count-len(self.patterns)
        summary_str =(f'\n----- Finished creating database -----'
                      f'\n{num_unsuccessful}/{self.total_count} patterns could not be parsed')


        num_crit, num_err, num_warn = 0,0,0
        reports = [pattern.processing_report for pattern in self.patterns]
        for report in reports:
            num_crit += report.has_critical_error()
            num_err += report.has_error()
            num_warn += report.has_warning()

        summary_str += f'\n{num_crit}/{self.total_count} patterns had critical error(s)'
        summary_str += f'\n{num_err}/{self.total_count}  patterns had error(s)'
        summary_str += f'\n{num_warn}/{self.total_count}  patterns had warning(s)'
        log(f'{summary_str}\n\n'
            f'----------------------------------------\n')

        log(f'Individual file reports\n\n')
        for pattern in self.patterns:
            log(msg=str(pattern.processing_report))


    def copy_datafiles(self, target_dir : str):
        os.makedirs(target_dir, exist_ok=True)
        for path in self.get_data_fpaths():
            filename = find_free_path(dirpath=target_dir, basename=os.path.basename(path))
            fpath = os.path.join(target_dir, filename)
            shutil.copy(path, fpath)


    def get_data_fpaths(self) -> list[str]:
        root_node = FsysNode(path=self.root_path)
        xrd_files_nodes = root_node.get_file_subnodes(select_formats=allowed_suffixes)
        return [node.get_path() for node in xrd_files_nodes]


def find_free_path(dirpath: str, basename: str):
    while True:
        smol_uuid4 = str(uuid4())[:5]
        fpath = f'{smol_uuid4}_{basename}'
        if not fpath in os.listdir(path=dirpath):
            return fpath
