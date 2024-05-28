from __future__ import annotations

import os.path
from typing import Optional, Iterator, Tuple
from dataclasses import dataclass
from holytools.fsys import SaveManager
from xrdpattern.core import PatternData
from .data_files import XrdFormat, Formats, get_xylib_repr
from .csv import CsvParser, Orientation
from xrdpattern.parsing.stoe import StoeReader
from ..powder import PatternLabel, Artifacts


# -------------------------------------------

@dataclass
class ParserOptions:
    select_suffixes : Optional[list[str]] = None
    default_wavelength : Optional[float] = None
    pattern_data_orientation : Orientation = Orientation.VERTICAL


class Parser:
    def __init__(self, parser_options : ParserOptions = ParserOptions()):
        if parser_options.select_suffixes is None:
            self.select_formats : list[str] = Formats.get_allowed_suffixes()
        self.default_wavelength_angstr : Optional[float] = parser_options.default_wavelength
        self.stoe_reader : StoeReader = StoeReader()

    # -------------------------------------------
    # pattern

    def get_pattern_info_list(self, fpath : str) -> list[PatternData]:
        suffix = SaveManager.get_suffix(fpath)
        if not suffix in Formats.get_allowed_suffixes():
            raise ValueError(f"File {fpath} has unsupported format .{suffix}")
        if suffix:
            the_format = Formats.get_format(fpath)
        else:
            raise ValueError(f"Could not determine file format of \"{fpath}\": Invalid suffix {suffix}")

        if the_format == Formats.aimat_json:
            pattern_infos = [self.from_json(fpath=fpath)]
        elif the_format == Formats.stoe_raw:
            pattern_infos = [self.stoe_reader.get_pattern_info(fpath=fpath)]
        elif the_format.suffix in Formats.get_datafile_suffixes():
            pattern_infos = [self.from_data_file(fpath=fpath, format_hint=the_format)]
        elif the_format == Formats.csv:
            pattern_infos = self.from_csv(fpath=fpath)
        else:
            raise ValueError(f"Format .{the_format} is not supported")
        for pattern in pattern_infos:
            if pattern.label.primary_wavelength is None and self.default_wavelength_angstr:
                pattern.label.artifacts.primary_wavelength = self.default_wavelength_angstr
        for info in pattern_infos:
            info.name = os.path.basename(fpath)
        return pattern_infos


    @staticmethod
    def from_json(fpath: str) -> PatternData:
        with open(fpath, 'r') as file:
            data = file.read()
            new_pattern = PatternData.from_str(json_str=data)
        return new_pattern


    @staticmethod
    def from_data_file(fpath: str, format_hint : XrdFormat) -> PatternData:
        xylib_repr = get_xylib_repr(fpath=fpath, format_hint=format_hint)
        header,data_str = xylib_repr.get_header(), xylib_repr.get_data()
        metadata = Parser.parse_xylib_header(header_str=header)

        angles, intensities= [], []
        data_rows = [row for row in data_str.split('\n') if not row.strip() == '']
        for row in data_rows:
            deg_str, intensity_str = row.split()
            deg, intensity = float(deg_str), float(intensity_str)
            angles.append(deg)
            intensities.append(intensity)
        return PatternData(two_theta_values=angles, intensities=intensities, label=metadata)


    @staticmethod
    def from_csv(fpath : str) -> list[PatternData]:
        if CsvParser.has_two_columns(fpath=fpath):
            orientation = Orientation.VERTICAL
        else:
            print(f'''Please specify along which the data of individual patterns is oriented in {fpath}'
                  E.g. in the below example the data is oriented vertically
                       x y
                       5 1000
                       10 2000
                       15 1500''')
            orientation = Orientation.from_manual_query()

        csv_parser = CsvParser(pattern_data_axis=orientation)
        pattern_infos = csv_parser.read_csv(fpath=fpath)
        return pattern_infos


    # -------------------------------------------
    # parsing xylib header

    @classmethod
    def parse_xylib_header(cls, header_str: str) -> PatternLabel:
        metadata_map = cls.get_key_value_dict(header_str=header_str)

        def get_float(key: str) -> Optional[float]:
            val = metadata_map.get(key)
            if val:
                val = float(val)
            return val

        experiment = PatternLabel.make_empty()
        experiment.artifacts = Artifacts(
            primary_wavelength=get_float('ALPHA1'),
            secondary_wavelength=get_float('ALPHA2'),
            secondary_to_primary=get_float('ALPHA_RATIO')
        )
        experiment.powder.temp_in_kelvin = get_float('TEMP_CELCIUS') + 273.15

        return experiment

    @staticmethod
    def get_key_value_dict(header_str: str) -> dict:
        key_value_dict = {}
        for key, value in Parser.get_key_value_pairs(header_str):
            key_value_dict[key] = value
        return key_value_dict

    @staticmethod
    def get_key_value_pairs(header_str: str) -> Iterator[Tuple[str, str]]:
        commented_lines = [line for line in header_str.splitlines() if line.startswith('#')]
        for line in commented_lines:
            key_value = line[1:].split(':', 1)
            if len(key_value) == 2:
                yield key_value[0].strip(), key_value[1].strip()