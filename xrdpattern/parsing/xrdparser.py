from __future__ import annotations
from typing import Optional
from dataclasses import dataclass
from hollarek.fsys import FsysNode

from ..core import PatternInfo, Metadata, IntensityMap, XAxisType
from .data_files import XrdFormat, Formats, get_xylib_repr
from .csv import CsvScheme, CsvReader

# -------------------------------------------

@dataclass
class ParserOptions:
    select_suffixes : Optional[list[str]] = None
    csv_scheme : Optional[CsvScheme] = None
    format_hint : Optional[XrdFormat] = None
    default_wavelength_angstr : Optional[float] = None


class XrdParser:
    def __init__(self, parser_options : ParserOptions = ParserOptions()):
        if parser_options.select_suffixes is None:
            self.select_formats : list[str] = Formats.get_allowed_suffixes()
        self.format_hint : Optional[XrdFormat] = parser_options.format_hint
        self.default_wavelength_angstr : Optional[float] = parser_options.default_wavelength_angstr
        self.default_csv_reader : Optional[CsvReader] = CsvReader(parser_options.csv_scheme)

    # -------------------------------------------
    # pattern database

    # def get_pattern_db(self, datafolder_path : str) -> PatternInfoDB:
    #     if not os.path.isdir(datafolder_path):
    #         raise ValueError(f"Given path {datafolder_path} is not a directory")
    #
    #     patterns = []
    #     data_fpaths = self.get_datafile_fpaths(datafolder_path=datafolder_path)
    #     for fpath in data_fpaths:
    #         try:
    #             new_patterns = self.get_patterns(fpath=fpath)
    #             patterns += new_patterns
    #         except Exception as e:
    #             print(f"Could not import pattern from file {fpath} \n"
    #                   f"-> Error: \"{e.__class__.__name__}: {str(e)}\"")
    #     return PatternInfoDB(patterns=patterns)


    # def get_datafile_fpaths(self, datafolder_path : str) -> list[str]:
    #     root_node = FsysNode(path=datafolder_path)
    #     xrd_files_nodes = root_node.get_file_subnodes(select_formats=self.select_formats)
    #     return [node.get_path() for node in xrd_files_nodes]

    # -------------------------------------------
    # pattern

    def get_pattern_info_list(self, fpath : str) -> list[PatternInfo]:
        suffix = FsysNode(fpath).get_suffix()

        if suffix == Formats.aimat_json.suffix:
            xrd_pattern = [self.from_json(fpath=fpath)]
        elif suffix in Formats.get_datafile_suffixes():
            format_hint = self.format_hint
            if not format_hint:
                format_hint = Formats.get_format(suffix=suffix)
            xrd_pattern = [self.from_data_file(fpath=fpath, format_hint=format_hint)]
        elif suffix == 'csv':
            xrd_pattern = self.from_csv(fpath=fpath)
        else:
            raise ValueError(f"Unable to determine format of file {fpath} without format hint or file extension")
        for pattern in xrd_pattern:
            if pattern.get_wavelength(primary=True) is None and self.default_wavelength_angstr:
                pattern.set_wavelength(new_wavelength=self.default_wavelength_angstr)

        return xrd_pattern


    @staticmethod
    def from_json(fpath: str) -> PatternInfo:
        with open(fpath, 'r') as file:
            data = file.read()
            new_pattern = PatternInfo.from_str(json_str=data)
        return new_pattern


    @staticmethod
    def from_data_file(fpath: str, format_hint : XrdFormat) -> PatternInfo:
        xylib_repr = get_xylib_repr(fpath=fpath, format_hint=format_hint)
        header,data_str = xylib_repr.get_header(), xylib_repr.get_data()
        metadata = Metadata.from_header_str(header_str=header)

        two_theta_to_intensity = {}
        data_rows = [row for row in data_str.split('\n') if not row.strip() == '']
        for row in data_rows:
            deg_str, intensity_str = row.split()
            deg, intensity = float(deg_str), float(intensity_str)
            two_theta_to_intensity[deg] = intensity
        intensity_map = IntensityMap(data=two_theta_to_intensity, x_axis_type=XAxisType.TwoTheta)
        return PatternInfo(intensity_map=intensity_map, metadata=metadata)


    def from_csv(self, fpath : str, csv_scheme : Optional[CsvScheme] = None) -> list[PatternInfo]:
        csv_reader = None
        if csv_scheme:
            csv_reader = CsvReader(csv_scheme)
        if self.default_csv_reader:
            csv_reader = self.default_csv_reader
        if not csv_reader:
            print(f'No CSV scheme specified in either argument or as default value of xrdparser.'
                  f'Please specify csv scheme for {fpath} manually:')
            csv_reader = CsvReader(CsvScheme.from_manual())
        return csv_reader.read_csv(fpath=fpath)




