import os.path
import os
from uuid import uuid4

from xrdpattern.xrd_file_io import find_all_parsable_files
from xrdpattern.xrd_logger import log_xrd_info
from .pattern import XrdPattern

class XrdPatternDB:
    def __init__(self):
        self.patterns : list[XrdPattern] = []


    def import_data(self, dir_path : str):
        if not os.path.isdir(dir_path):
            raise ValueError(f"Given path {dir_path} is not a directory")
        for file_path in find_all_parsable_files(dir_path=dir_path):
            try:
                new_pattern = XrdPattern(filepath=file_path)
                self.patterns.append(new_pattern)
            except Exception as e:
                log_xrd_info(f"Could not import pattern from file {file_path}. Error: {str(e)}")


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
        