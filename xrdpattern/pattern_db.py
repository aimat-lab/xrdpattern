import os.path
from xrd_file_io import find_all_parsable_files
from .xrd_pattern import XrdPattern
from xrd_logger import log_xrd_info



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


    def export_data(self):
        pass