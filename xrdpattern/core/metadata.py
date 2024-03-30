from __future__ import annotations
from datetime import datetime
from typing import Optional
from hollarek.abstract import JsonDataclass
from dataclasses import dataclass

from typing import Iterator, Tuple


# -------------------------------------------


@dataclass
class WavelengthInfo(JsonDataclass):
    primary: float
    secondary: Optional[float] = None
    ratio: Optional[float] = None

    def __eq__(self, other):
        return self.primary == other.primary and self.secondary == other.secondary and self.ratio == other.ratio

@dataclass
class Metadata(JsonDataclass):
    wavelength_info: Optional[WavelengthInfo]
    anode_material: Optional[str] = None
    temp_celcius: Optional[float] = None
    measurement_date: Optional[datetime] = None

    @classmethod
    def make_empty(cls):
        return Metadata(wavelength_info=None)

    @classmethod
    def from_wavelength(cls, primary_wavelength : float, secondary_wavelength : Optional[float] = None):
        return cls(wavelength_info=WavelengthInfo(primary_wavelength, secondary_wavelength))

    @classmethod
    def from_header_str(cls, header_str: str) -> Metadata:
        metadata_map = cls.get_key_value_dict(header_str=header_str)

        def get_float(key: str) -> Optional[float]:
            val = metadata_map.get(key)
            if val:
                val = float(val)
            return val

        wavelength_info = WavelengthInfo(primary=get_float('ALPHA1'),
                                         secondary=get_float('ALPHA2'),
                                         ratio=get_float('ALPHA_RATIO')
                                         )

        metadata = cls(
            wavelength_info=wavelength_info,
            anode_material=metadata_map.get('ANODE_MATERIAL'),
            temp_celcius=get_float('TEMP_CELCIUS'),
            measurement_date=cls.get_date_time(metadata_map.get('MEASURE_DATE'), metadata_map.get('MEASURE_TIME'))
        )

        return metadata

    @classmethod
    def get_key_value_dict(cls, header_str: str) -> dict:
        key_value_dict = {}
        for key, value in cls.get_key_value_pairs(header_str):
            key_value_dict[key] = value
        return key_value_dict

    @staticmethod
    def get_key_value_pairs(header_str: str) -> Iterator[Tuple[str, str]]:
        commented_lines = [line for line in header_str.splitlines() if line.startswith('#')]
        for line in commented_lines:
            key_value = line[1:].split(':', 1)
            if len(key_value) == 2:
                yield key_value[0].strip(), key_value[1].strip()

    @staticmethod
    def get_date_time(date_str: str, time_str: str) -> Optional[datetime]:
        if date_str and time_str:
            combined_str = date_str + ' ' + time_str
            return datetime.strptime(combined_str, '%m/%d/%Y %H:%M:%S')
        return None


    def __eq__(self, other):
        wavelength_match = self.wavelength_info == other.wavelength_info
        anode_match = self.anode_material == other.anode_material
        temp_match = self.temp_celcius == other.temp_celcius
        date_match = self.measurement_date == other.measurement_date

        return wavelength_match and anode_match and temp_match and date_match