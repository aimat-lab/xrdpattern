import os.path
import os
from uuid import uuid4
from xrdpattern.xrd_file_io import find_all_parsable_files
from xrdpattern.xrd_logger import log_xrd_info
from .pattern import XrdPattern
from typing import Optional

# -------------------------------------------

class XrdPatternDB:
    def __init__(self, log_file_path : Optional[str] = None):
        self.patterns : list[XrdPattern] = []
        self.log_file_path : Optional[str] = log_file_path
        self.num_unsuccessful : int = 0
        self.total_count : int = 0

    def import_data(self, dir_path : str):
        if not os.path.isdir(dir_path):
            raise ValueError(f"Given path {dir_path} is not a directory")
        for file_path in find_all_parsable_files(dir_path=dir_path):
            try:
                new_pattern = XrdPattern(filepath=file_path, log_file_path = self.log_file_path)
                self.patterns.append(new_pattern)
            except Exception as e:
                self.num_unsuccessful += 1
                self.log(f"Could not import pattern from file {file_path}. Error: {str(e)}")
            finally:
                self.total_count += 1
        self.log(msg=self.get_db_report())

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

    def get_db_report(self):
        report_str = f'\n--- Finished creating database ---'
        report_str += f'\n{self.num_unsuccessful}/{self.total_count} patterns could not be parsed'

        patterns_with_crticials = [pattern for pattern in self.patterns if len(pattern.processing_report.critical_errors) == 0]
        patterns_with_errors = [pattern for pattern in self.patterns if len(pattern.processing_report.errors) == 0]
        patterns_with_warnings = [pattern for pattern in self.patterns if len(pattern.processing_report.warnings) == 0]

        report_str += f'\n{patterns_with_crticials}/{self.total_count} patterns had critical error(s)'
        report_str += f'\n{patterns_with_errors}/{self.total_count}  patterns had error(s)'
        report_str += f'\n{patterns_with_warnings}/{self.total_count}  patterns had warning(s)'

        return report_str
