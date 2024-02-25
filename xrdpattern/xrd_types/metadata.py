from __future__ import annotations
from datetime import datetime
from typing import Optional
from serialization import SerializableDataclass
from dataclasses import dataclass

from typing import Iterator, Tuple

# -------------------------------------------

@dataclass
class Metadata(SerializableDataclass):
    prim_wavelength_angstr: Optional[float]
    sec_wavelength_angstr: Optional[float]
    prim_to_sec_ratio: Optional[float]
    anode_material: Optional[str] = None
    measured_on: Optional[datetime] = None
    temperature_celcius : Optional[float] = None

    @classmethod
    def from_header_str(cls, header_str : str) -> Metadata:
        values = cls.get_key_value_dict(header_str=header_str)
        metadata = cls(prim_wavelength_angstr=float(values['ALPHA1']) if 'ALPHA1' in values else None,
                       sec_wavelength_angstr=float(values['ALPHA2']) if 'ALPHA2' in values else None,
                       prim_to_sec_ratio=float(values['ALPHA_RATIO']) if 'ALPHA_RATIO' in values else None,
                       anode_material=values.get('ANODE_MATERIAL', None),
                       measured_on= cls.get_date_time(values.get('MEASURE_DATE'), values.get('MEASURE_TIME')))
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
