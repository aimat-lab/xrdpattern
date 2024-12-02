from __future__ import annotations

import os.path
from typing import Optional, Iterator, Tuple

import numpy as np

from holytools.fsys import SaveManager
from xrdpattern.xrd import PatternData, XRayInfo, PowderExperiment, Metadata
from xrdpattern.parsing.stoe import StoeParser
from .cif.cif_parser import CifParser
from .csv import CsvParser, Orientation
from .formats import XrdFormat, Formats
from .xylib import get_xylib_repr

# -------------------------------------------


class MasterParser:
    def __init__(self, csv_orientation : Optional[Orientation] = None):
        self.default_csv_orientation : Optional[Orientation] = csv_orientation

        self.stoe_reader : StoeParser = StoeParser()
        self.cif_parser : CifParser = CifParser()
        self.csv_parser : CsvParser = CsvParser()

    # -------------------------------------------
    # pattern

    def extract(self, fpath : str) -> list[PatternData]:
        suffix = SaveManager.get_suffix(fpath)
        if not suffix in Formats.get_all_suffixes():
            raise ValueError(f"File {fpath} has unsupported format .{suffix}")
        if suffix:
            the_format = Formats.get_format(fpath)
        else:
            raise ValueError(f"Could not determine file format of \"{fpath}\": Invalid suffix {suffix}")

        if the_format == Formats.aimat_xrdpattern:
            pattern_infos = [self.load_json(fpath=fpath)]
        elif the_format == Formats.pdcif:
            pattern_infos = [self.load_cif(fpath=fpath)]
        elif the_format == Formats.stoe_raw:
            pattern_infos = [self.stoe_reader.get_pattern_info(fpath=fpath)]
        elif the_format in Formats.get_datafile_formats():
            pattern_infos = [self.load_data_file(fpath=fpath, format_hint=the_format)]
        elif the_format == Formats.csv:
            pattern_infos = self.load_csv(fpath=fpath)
        else:
            raise ValueError(f"Format .{the_format} is not supported")
        for info in pattern_infos:
            info.name = os.path.basename(fpath)

        for p in pattern_infos:
            if not the_format == Formats.aimat_xrdpattern:
                p.metadata.original_file_format = f'{the_format.name} (.{suffix})'
                p.metadata.filename = os.path.basename(fpath)
        return pattern_infos


    @staticmethod
    def load_json(fpath: str) -> PatternData:
        with open(fpath, 'r') as file:
            data = file.read()
            new_pattern = PatternData.from_str(json_str=data)
        return new_pattern


    @staticmethod
    def load_data_file(fpath: str, format_hint : XrdFormat) -> PatternData:
        xylib_repr = get_xylib_repr(fpath=fpath, format_hint=format_hint)
        header,data_str = xylib_repr.get_header(), xylib_repr.get_data()
        powder_experiment = MasterParser.parse_experiment_params(header_str=header)
        metadata = MasterParser.parse_metadata(header_str=header)

        two_theta_values, intensities= [], []
        data_rows = [row for row in data_str.split('\n') if not row.strip() == '']
        for row in data_rows:
            deg_str, intensity_str = row.split()
            deg, intensity = float(deg_str), float(intensity_str)
            two_theta_values.append(deg)
            intensities.append(intensity)

        two_theta_values, intensities = np.array(two_theta_values), np.array(intensities)
        return PatternData(two_theta_values=two_theta_values, intensities=intensities, powder_experiment=powder_experiment, metadata=metadata)


    def load_csv(self, fpath : str) -> list[PatternData]:
        if CsvParser.has_two_columns(fpath=fpath):
            orientation = Orientation.VERTICAL
        elif self.default_csv_orientation is not None:
            orientation = self.default_csv_orientation
        else:
            raise ValueError(f"Could not determine orientation of data in csv file {fpath}")

        pattern_infos = self.csv_parser.extract_patterns(fpath=fpath, pattern_dimension=orientation)
        return pattern_infos

    def load_cif(self, fpath : str) -> PatternData:
        return self.cif_parser.extract_pattern(fpath=fpath)

    # -------------------------------------------
    # databases xylib header

    @classmethod
    def parse_experiment_params(cls, header_str: str) -> PowderExperiment:
        metadata_map = cls.get_key_value_dict(header_str=header_str)

        def get_float(key: str) -> Optional[float]:
            val = metadata_map.get(key)
            if val:
                val = float(val)
            return val

        experiment = PowderExperiment.make_empty()
        experiment.xray_info = XRayInfo(primary_wavelength=get_float('ALPHA1'), secondary_wavelength=get_float('ALPHA2'))
        experiment.temp_in_celcius = get_float('TEMP_CELCIUS')

        return experiment

    @classmethod
    def parse_metadata(cls, header_str : str) -> Metadata:
        metadata_map = cls.get_key_value_dict(header_str=header_str)
        metadata = Metadata(measurement_date=metadata_map.get('MEASURE_DATE'))
        return metadata

    @staticmethod
    def get_key_value_dict(header_str: str) -> dict:
        key_value_dict = {}
        for key, value in MasterParser.get_key_value_pairs(header_str):
            key_value_dict[key] = value
        return key_value_dict

    @staticmethod
    def get_key_value_pairs(header_str: str) -> Iterator[Tuple[str, str]]:
        commented_lines = [line for line in header_str.splitlines() if line.startswith('#')]
        for line in commented_lines:
            key_value = line[1:].split(':', 1)
            if len(key_value) == 2:
                yield key_value[0].strip(), key_value[1].strip()


