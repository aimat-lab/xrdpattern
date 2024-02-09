from datetime import datetime
from typing import Optional


class Metadata:
    def __init__(self, header_str: str):
        key_value_dict = self.get_key_value_dict(header_str)

        self.primary_wavelength_angstrom: float = float(key_value_dict.get('ALPHA1', 0))
        self.secondary_wavelength_angstrom: Optional[float] = float(key_value_dict.get('ALPHA2', 0))
        self.primary_to_secondary_ratio: Optional[float] = float(key_value_dict.get('ALPHA_RATIO', 0))
        self.anode_material: Optional[str] = key_value_dict.get('ANODE_MATERIAL', '')
        self.measurement_datetime: Optional[datetime] = self.get_date_time(key_value_dict.get('MEASURE_DATE'),
                                                                           key_value_dict.get('MEASURE_TIME'))

    def get_key_value_dict(self,header_str: str) -> dict:
        key_value_dict = {}
        for key, value in self.get_key_value_pairs(header_str):
            key_value_dict[key] = value
        return key_value_dict

    @staticmethod
    def get_key_value_pairs(header_str: str):
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
