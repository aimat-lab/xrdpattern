from __future__ import annotations
import os.path
from typing import Optional
from dataclasses import dataclass
from hollarek.fsys import FsysNode

from xrdpattern.pattern import XrdPattern, Metadata
from xrdpattern.database import XrdPatternDB
from .data_files import XrdFormat, Formats, get_xylib_repr
from .csv import CsvScheme

# -------------------------------------------

@dataclass
class ParserOptions:
    select_suffixes : Optional[list[str]] = None
    csv_scheme : Optional[CsvScheme] = None
    format_hint : Optional[XrdFormat] = None
    wave_length_angstrom : Optional[float] = None


class XrdParser:
    def __init__(self, parser_options : ParserOptions = ParserOptions()):
        if parser_options.select_suffixes is None:
            self.select_formats : list[str] = Formats.get_allowed_suffixes()
        self.csv_scheme : Optional[CsvScheme] =  parser_options.csv_scheme
        self.format_hint : Optional[XrdFormat] = parser_options.format_hint

    # -------------------------------------------
    # pattern

    def get_patterns(self, fpath : str) -> list[XrdPattern]:
        suffix = FsysNode(fpath).get_suffix()

        if suffix == Formats.aimat_json.suffix:
            patterns = [self.from_json(fpath=fpath)]
        elif suffix in Formats.get_datafile_suffixes():
            format_hint = self.format_hint
            if not format_hint:
                format_hint = Formats.get_format(suffix=suffix)
            patterns = [self.from_data_file(fpath=fpath, format_hint=format_hint)]
        elif suffix == 'csv':
            csv_scheme = self.csv_scheme
            if not csv_scheme:
                print(f'No csv scheme specified for {fpath}')
                csv_scheme = CsvScheme.from_manual()
            patterns = self.from_csv(fpath=fpath, csv_scheme=csv_scheme)
        else:
            raise ValueError(f"Unable to determine format of file {fpath} without format hint or file extension")
        return patterns


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


    @staticmethod
    def from_csv(fpath : str, csv_scheme : CsvScheme):
        raise NotImplementedError

    # -------------------------------------------
    # pattern database

    def get_pattern_db(self, datafolder_path : str) -> XrdPatternDB:
        if not os.path.isdir(datafolder_path):
            raise ValueError(f"Given path {datafolder_path} is not a directory")

        patterns = []
        data_fpaths = self.get_datafile_fpaths(datafolder_path=datafolder_path)
        for fpath in data_fpaths:
            try:
                new_patterns = self.get_patterns(fpath=fpath)
                patterns += new_patterns
            except Exception as e:
                print(f"Could not import pattern from file {fpath}. Error: {str(e)}")
        return XrdPatternDB(patterns=patterns)


    def preprocess_csv(self, datafolder_path : str, scheme : CsvScheme):
        raise NotImplementedError


    def get_datafile_fpaths(self, datafolder_path : str) -> list[str]:
        root_node = FsysNode(path=datafolder_path)
        xrd_files_nodes = root_node.get_file_subnodes(select_formats=self.select_formats)
        return [node.get_path() for node in xrd_files_nodes]



