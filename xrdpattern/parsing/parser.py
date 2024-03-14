from __future__ import annotations
import re
import os.path
from typing import Optional
from hollarek.fsys import FsysNode

from xrdpattern.pattern import XrdPattern, Metadata
from xrdpattern.database import XrdPatternDB
from .data_formats import Formats, XrdFormat
from .xylib_repr import get_xylib_repr
# -------------------------------------------



class Parser:
    def __init__(self, select_suffixes : Optional[list[str]] = None):
        if select_suffixes is None:
            self.select_formats : list[str] = Formats.get_allowed_suffixes()

    # -------------------------------------------
    # pattern

    def get_pattern(self, fpath : str, format_hint : Optional[XrdFormat] = None) -> XrdPattern:
        suffix = FsysNode(fpath).get_suffix()

        if suffix == Formats.aimat_json.suffix:
            pattern = self.from_json(fpath=fpath)
        elif suffix:
            if not format_hint:
                format_hint = Formats.get_format(suffix=suffix)
            pattern = self.from_data_file(fpath=fpath, format_hint=format_hint)
        else:
            raise ValueError(f"Unable to determine format of file {fpath} without format hint or file extension")
        return pattern

    @staticmethod
    def from_json(fpath: str) -> XrdPattern:
        with open(fpath, 'r') as file:
            data = file.read()
            new_pattern = XrdPattern.from_str(json_str=data)
        return new_pattern


    @staticmethod
    def from_data_file(fpath: str, format_hint : XrdFormat) -> XrdPattern:
        xylib_repr = get_xylib_repr(fpath=fpath, format_hint=format_hint)
        header,data_str = xylib_repr.get_header(), xylib_repr.get_data()
        metadata = Metadata.from_header_str(header_str=header)

        twotheta_to_intensity = {}
        data_rows = [row for row in data_str.split('\n') if not row.strip() == '']
        for row in data_rows:
            deg_str, intensity_str = row.split()
            deg, intensity = float(deg_str), float(intensity_str)
            twotheta_to_intensity[deg] = intensity

        return XrdPattern(twotheta_to_intensity=twotheta_to_intensity, metadata=metadata)

    # -------------------------------------------
    # pattern database

    def get_pattern_db(self, datafolder_path : str) -> XrdPatternDB:
        if not os.path.isdir(datafolder_path):
            raise ValueError(f"Given path {datafolder_path} is not a directory")

        patterns = []
        data_fpaths = self.get_datafile_fpaths(datafolder_path=datafolder_path)
        # total_count = len(data_fpaths)
        for fpath in data_fpaths:
            try:
                new_pattern = self.get_pattern(fpath=fpath)
                patterns.append(new_pattern)
            except Exception as e:
                print(f"Could not import pattern from file {fpath}. Error: {str(e)}")
        return XrdPatternDB(patterns=patterns)


    def get_datafile_fpaths(self, datafolder_path : str) -> list[str]:
        root_node = FsysNode(path=datafolder_path)
        xrd_files_nodes = root_node.get_file_subnodes(select_formats=self.select_formats)
        return [node.get_path() for node in xrd_files_nodes]

