from __future__ import annotations

import os.path
from typing import Optional
from dataclasses import dataclass
from hollarek.fsys import SaveManager
from ..core import PatternInfo, Metadata, XrdIntensities, XAxisType
from .data_files import XrdFormat, Formats, get_xylib_repr
from .csv import CsvScheme, CsvParser

# -------------------------------------------

@dataclass
class ParserOptions:
    select_suffixes : Optional[list[str]] = None
    csv_scheme : Optional[CsvScheme] = None
    default_format_hint : Optional[XrdFormat] = None
    default_wavelength_angstr : Optional[float] = None


class Parser:
    def __init__(self, parser_options : ParserOptions = ParserOptions()):
        if parser_options.select_suffixes is None:
            self.select_formats : list[str] = Formats.get_allowed_suffixes()
        self.default_format : Optional[XrdFormat] = parser_options.default_format_hint
        self.default_wavelength_angstr : Optional[float] = parser_options.default_wavelength_angstr
        self.default_csv_reader : Optional[CsvParser] = None

    # -------------------------------------------
    # pattern

    def get_pattern_info_list(self, fpath : str) -> list[PatternInfo]:
        suffix = SaveManager.get_suffix(fpath)
        if not suffix in Formats.get_allowed_suffixes():
            raise ValueError(f"File {fpath} has unsupported format .{suffix}")
        if suffix:
            the_format = Formats.get_format(suffix)
        elif not self.default_format is None:
            the_format = self.default_format
        else:
            raise ValueError(f"Could not determine file format of \"{fpath}\" since not default format"
                             f"was specified and file does not have suffix indicating format")

        if the_format == Formats.aimat_json:
            pattern_infos = [self.from_json(fpath=fpath)]
        elif the_format.suffix in Formats.get_datafile_suffixes():
            pattern_infos = [self.from_data_file(fpath=fpath, format_hint=the_format)]
        elif the_format == Formats.csv:
            pattern_infos = self.from_csv(fpath=fpath)
        else:
            raise ValueError(f"Format .{the_format} is not supported")
        for pattern in pattern_infos:
            if pattern.get_wavelength(primary=True) is None and self.default_wavelength_angstr:
                pattern.set_wavelength(new_wavelength=self.default_wavelength_angstr)
        for info in pattern_infos:
            info.name = os.path.basename(fpath)
        return pattern_infos


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
        intensity_map = XrdIntensities(data=two_theta_to_intensity, x_axis_type=XAxisType.TwoTheta)
        return PatternInfo(xrd_intensities=intensity_map, metadata=metadata)


    def from_csv(self, fpath : str, csv_scheme : Optional[CsvScheme] = None) -> list[PatternInfo]:
        csv_reader = None
        if csv_scheme:
            csv_reader = CsvParser(csv_scheme)
        if self.default_csv_reader:
            csv_reader = self.default_csv_reader
        if not csv_reader:
            print(f'No CSV scheme specified in either argument or as default value of xrdparser.'
                  f'Please specify csv scheme for {fpath} manually\n'
                  f'- XAxisType: Whether x-axis is TwoTheta values or Q values\n'
                  f'- Orientation: Along which axis different patterns are listed:')
            csv_reader = CsvParser(CsvScheme.from_manual())
        return csv_reader.read_csv(fpath=fpath)

