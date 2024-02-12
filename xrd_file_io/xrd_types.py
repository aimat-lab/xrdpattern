from __future__ import annotations
from datetime import datetime
from typing import Optional
from serialization import SerializableDataclass
from dataclasses import dataclass

from typing import Iterator, Tuple


class XrdFormat:
    def __init__(self, name : str, suffix :str):
        self.name : str = name
        # suffix is "csv" not ".csv"
        self.suffix : str = suffix


class XYLibOption:
    def __init__(self, input_path : str, output_path : str, input_type : Optional[XrdFormat] = None):
        self.INPUT_FILE : str = input_path
        self.OUTPUT_PATH : str = output_path
        self.INPUT_TYPE : Optional[XrdFormat] = input_type


class Formats:
    bruker_raw = XrdFormat("bruker_raw", "raw")
    bruker_spc = XrdFormat("bruker_spc", "spc")
    canberra_cnf = XrdFormat("canberra_cnf", "cnf")
    canberra_mca = XrdFormat("canberra_mca", "mca")
    chiplot = XrdFormat("chiplot", "chiplot")
    cpi = XrdFormat("cpi", "cpi")
    csv = XrdFormat("csv", "csv")
    dbws = XrdFormat("dbws", "dbw")
    pdcif = XrdFormat("pdcif", "cif")
    philips_raw = XrdFormat("philips_raw", "rd")
    philips_udf = XrdFormat("philips_udf", "udf")
    riet7 = XrdFormat("riet7", "dat")
    rigaku_dat = XrdFormat("rigaku_dat", "dat")
    specsxy = XrdFormat("specsxy", "specsxy")
    spectra = XrdFormat("spectra", "spectra")
    text = XrdFormat("text", "txt")
    uxd = XrdFormat("uxd", "uxd")
    vamas = XrdFormat("vamas", "vms")
    winspec_spe = XrdFormat("winspec_spe", "spe")
    xfit_xdd = XrdFormat("xfit_xdd", "xdd")
    xrdml = XrdFormat("xrdml", "xrdml")
    xsyg = XrdFormat("xsyg", "xsyg")
    aimat_json = XrdFormat("ajson","json")

allowed_suffix_types = [xrd_format.suffix for xrd_format in Formats.__dict__.values() if isinstance(xrd_format, XrdFormat)]


class Mapping(dict[float,float]):
    pass


@dataclass
class Metadata(SerializableDataclass):
    primary_wavelength_angstrom: Optional[float]
    secondary_wavelength_angstrom: Optional[float]
    primary_to_secondary_ratio: Optional[float]
    anode_material: Optional[str]
    measurement_datetime: Optional[datetime]

    @classmethod
    def from_header_str(cls, header_str : str) -> Metadata:
        key_value_dict = cls.get_key_value_dict(header_str=header_str)
        metadata = cls(primary_wavelength_angstrom = float(key_value_dict.get('ALPHA1', 0)),
            secondary_wavelength_angstrom = float(key_value_dict.get('ALPHA2', 0)),
            primary_to_secondary_ratio = float(key_value_dict.get('ALPHA_RATIO', 0)),
            anode_material = key_value_dict.get('ANODE_MATERIAL', ''),
            measurement_datetime = cls.get_date_time(key_value_dict.get('MEASURE_DATE'), key_value_dict.get('MEASURE_TIME'))
        )
        return metadata


    @classmethod
    def get_key_value_dict(cls,header_str: str) -> dict:
        key_value_dict = {}
        for key, value in cls.get_key_value_pairs(header_str):
            key_value_dict[key] = value
        return key_value_dict


    @staticmethod
    def get_key_value_pairs(header_str: str) -> Iterator[Tuple[str, str]]:
        commented_lines = [line for line in header_str.splitlines() if line.startswith('#')]
        for line in commented_lines:
            key_value = line[1:].split(':',1)
            if len(key_value) == 2:
                yield key_value[0].strip(), key_value[1].strip()

    @staticmethod
    def get_date_time(date_str: str, time_str: str) -> Optional[datetime]:
        if date_str and time_str:
            combined_str = date_str + ' ' + time_str
            return datetime.strptime(combined_str, '%m/%d/%Y %H:%M:%S')
        return None
