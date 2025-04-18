from __future__ import annotations

import os.path
import tempfile
from typing import Optional, Iterator, Tuple

import numpy as np

from xrdpattern.xrd import XrdData, XrayInfo, PowderExperiment, Metadata
from xrdpattern.parsing.stoe import StoeParser
from .cif.cif_parser import CifParser
from .csv import CsvParser
from .dat.dat_parser import DatParser
from .formats import XrdFormat, Formats
from .path_tools import PathTools
from .xylib import get_xylib_repr


# -------------------------------------------


class MasterParser:
    def __init__(self):
        self.stoe_reader : StoeParser = StoeParser()
        self.cif_parser : CifParser = CifParser()
        self.csv_parser : CsvParser = CsvParser()
        self.dat_parser : DatParser = DatParser()

    # -------------------------------------------
    # pattern

    def extract(self, fpath : str, csv_orientation : Optional[str] = None) -> list[XrdData]:
        suffix = PathTools.get_suffix(fpath)
        if not suffix in Formats.get_all_suffixes():
            raise ValueError(f"File {fpath} has unsupported format .{suffix}")
        if suffix:
            the_format = Formats.get_format(fpath)
        else:
            raise ValueError(f"Could not determine file format of \"{fpath}\": Invalid suffix {suffix}")

        if the_format == Formats.aimat_xrdpattern:
            pattern_infos = [self.load_json(fpath=fpath)]
        elif the_format == Formats.pdcif:
            pattern_infos = [self._load_cif(fpath=fpath)]
        elif the_format == Formats.stoe_raw:
            pattern_infos = [self.stoe_reader.extract(fpath=fpath)]
        elif the_format in Formats.get_xylib_formats():
            pattern_infos = [self._load_xylib_file(fpath=fpath, format_hint=the_format)]
        elif the_format == Formats.csv:
            pattern_infos = self._load_csv(fpath=fpath, orientation=csv_orientation)
        elif the_format == Formats.plaintext_dat:
            pattern_infos = self._load_plaintext_dat(fpath=fpath)
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
    def load_json(fpath: str) -> XrdData:
        with open(fpath, 'r') as file:
            data = file.read()
            new_pattern = XrdData.from_str(json_str=data)
        return new_pattern


    @staticmethod
    def _load_xylib_file(fpath: str, format_hint : XrdFormat) -> XrdData:
        xylib_repr = get_xylib_repr(fpath=fpath, format_name=format_hint.name)
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
        return XrdData(two_theta_values=two_theta_values, intensities=intensities, powder_experiment=powder_experiment, metadata=metadata)


    def _load_csv(self, fpath : str, orientation : Optional[str] = None) -> list[XrdData]:
        if PathTools.get_suffix(fpath) == 'xlsx':
            tmp_fpath = tempfile.mktemp(suffix='.csv')
            CsvParser.xlsx_to_csv(xlsx_fpath=fpath, csv_fpath=tmp_fpath)
            fpath = tmp_fpath
        if CsvParser.has_two_columns(fpath=fpath):
            orientation = 'vertical'
        if orientation is None:
            raise ValueError(f"Could not determine orientation of data in csv file {fpath}")

        return self.csv_parser.extract_multi(fpath=fpath, pattern_dimension=orientation)

    def _load_cif(self, fpath : str) -> XrdData:
        return self.cif_parser.extract(fpath=fpath)

    def _load_plaintext_dat(self, fpath : str) -> list[XrdData]:
        return self.dat_parser.extract_multi(fpath=fpath)

    # -------------------------------------------
    # special xylib header

    @classmethod
    def parse_experiment_params(cls, header_str: str) -> PowderExperiment:
        metadata_map = cls.get_key_value_dict(header_str=header_str)

        def get_float(key: str) -> Optional[float]:
            val = metadata_map.get(key)
            if val:
                val = float(val)
            return val

        experiment = PowderExperiment.make_empty()
        experiment.xray_info = XrayInfo(primary_wavelength=get_float('ALPHA1'), secondary_wavelength=get_float('ALPHA2'))
        experiment.temp_K = get_float('TEMP_CELCIUS')

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


