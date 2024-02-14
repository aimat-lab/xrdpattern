from __future__ import annotations
from datetime import datetime
from typing import Optional
from serialization import SerializableDataclass
from dataclasses import dataclass

from typing import Iterator, Tuple

# -------------------------------------------


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

        metadata = cls(primary_wavelength_angstrom=float(key_value_dict['ALPHA1']) if 'ALPHA1' in key_value_dict else None,
            secondary_wavelength_angstrom=float(key_value_dict['ALPHA2']) if 'ALPHA2' in key_value_dict else None,
            primary_to_secondary_ratio=float(key_value_dict['ALPHA_RATIO']) if 'ALPHA_RATIO' in key_value_dict else None,
            anode_material=key_value_dict.get('ANODE_MATERIAL', None),
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



