from __future__ import annotations

import os.path
from typing import Optional, Iterator, Tuple

import numpy as np

from holytools.fsys import SaveManager
from xrdpattern.xrd import PatternData, Artifacts, PowderExperiment
from xrdpattern.parsing.stoe import StoeParser
from .cif.cif_parser import CifParser
from .csv import CsvParser, Orientation
from .formats import XrdFormat, Formats
from .xylib import get_xylib_repr


# -------------------------------------------


class Parser:
    def __init__(self, default_wavelength : Optional[float] = None,
                 default_csv_orientation : Optional[Orientation] = None):
        self.default_wavelength_angstr : Optional[float] = default_wavelength
        self.default_csv_orientation : Optional[Orientation] = default_csv_orientation

        self.stoe_reader : StoeParser = StoeParser()
        self.cif_parser : CifParser = CifParser()
        self.csv_parser : CsvParser = CsvParser()

    # -------------------------------------------
    # pattern

    def extract(self, fpath : str) -> list[PatternData]:
        suffix = SaveManager.get_suffix(fpath)
        if not suffix in Formats.get_allowed_suffixes():
            raise ValueError(f"File {fpath} has unsupported format .{suffix}")
        if suffix:
            the_format = Formats.get_format(fpath)
        else:
            raise ValueError(f"Could not determine file format of \"{fpath}\": Invalid suffix {suffix}")

        if the_format == Formats.aimat_xrdpattern:
            pattern_infos = [self.from_json(fpath=fpath)]
        elif the_format == Formats.cif:
            pattern_infos = [self.from_cif(fpath=fpath)]
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

        two_theta_values, intensities= [], []
        data_rows = [row for row in data_str.split('\n') if not row.strip() == '']
        for row in data_rows:
            deg_str, intensity_str = row.split()
            deg, intensity = float(deg_str), float(intensity_str)
            two_theta_values.append(deg)
            intensities.append(intensity)

        two_theta_values, intensities = np.array(two_theta_values), np.array(intensities)
        return PatternData(two_theta_values=two_theta_values, intensities=intensities, label=metadata)


    def from_csv(self, fpath : str) -> list[PatternData]:
        if CsvParser.has_two_columns(fpath=fpath):
            orientation = Orientation.VERTICAL
        elif self.default_csv_orientation is not None:
            orientation = self.default_csv_orientation
        else:
            raise ValueError(f"Could not determine orientation of data in csv file {fpath}")

        pattern_infos = self.csv_parser.extract_patterns(fpath=fpath, pattern_dimension=orientation)
        return pattern_infos

    def from_cif(self, fpath : str) -> PatternData:
        return self.cif_parser.extract_pattern(fpath=fpath)

    # -------------------------------------------
    # parsing xylib header

    @classmethod
    def parse_xylib_header(cls, header_str: str) -> PowderExperiment:
        metadata_map = cls.get_key_value_dict(header_str=header_str)

        def get_float(key: str) -> Optional[float]:
            val = metadata_map.get(key)
            if val:
                val = float(val)
            return val

        experiment = PowderExperiment.make_empty()
        experiment.artifacts = Artifacts(primary_wavelength=get_float('ALPHA1'),secondary_wavelength=get_float('ALPHA2'))
        experiment.powder.temp_in_celcius = get_float('TEMP_CELCIUS')

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