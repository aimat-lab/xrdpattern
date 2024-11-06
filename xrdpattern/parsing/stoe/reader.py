import numpy as np

from xrdpattern.xrd import PatternData
from .quantities import Quantity, FloatQuantity, IntegerQuantity
from xrdpattern.xrd import Artifacts, PowderExperiment


class BinaryReader:
    def read(self, fpath : str):
        with open(fpath, 'rb') as f:
            byte_content = f.read()
        self.read_bytes(byte_content=byte_content)

    def read_bytes(self, byte_content : bytes):
        for key, value in self.__dict__.items():
            if isinstance(value, Quantity):
                value.extract_value(byte_content)


class StoeParser(BinaryReader):
    def __init__(self):
        self.primary_wavelength : FloatQuantity = FloatQuantity(start=326)
        self.secondary_wavelength : FloatQuantity = FloatQuantity(start=322)
        self.ratio : FloatQuantity = FloatQuantity(start=384)
        self.num_entries : IntegerQuantity = IntegerQuantity(start=2082)
        self.angle_start : FloatQuantity = FloatQuantity(start=572)
        self.angle_end : FloatQuantity = FloatQuantity(start=576)
        self.intensities : IntegerQuantity = IntegerQuantity(start=2560)


    def read(self, fpath : str):
        with open(fpath, 'rb') as f:
            byte_content = f.read()
        min_size = self.intensities.start+4
        if len(byte_content) < min_size:
            raise ValueError(f'File is too small. Expected at least {min_size} bytes, got {len(byte_content)} bytes')
        self.num_entries.extract_value(byte_content=byte_content)
        self.intensities.size = self.num_entries.get_value()
        super().read_bytes(byte_content=byte_content)


    def get_pattern_info(self, fpath : str) -> PatternData:
        self.read(fpath=fpath)
        experiment = PowderExperiment.make_empty()
        experiment.artifacts = Artifacts(primary_wavelength=self.primary_wavelength.get_value(),
                                         secondary_wavelength=self.secondary_wavelength.get_value())

        two_theta_values = self._get_x_values()
        intensities = self._get_y_values()

        two_theta_values, intensities = np.array(two_theta_values), np.array(intensities)
        return PatternData(two_theta_values=two_theta_values, intensities=intensities, label=experiment)


    def _get_x_values(self) -> list[float]:
        start_value = self.angle_start.get_value()
        end_value = self.angle_end.get_value()
        num_entries = self.num_entries.get_value()
        step = (end_value - start_value) / (num_entries - 1)
        return [start_value + i * step for i in range(num_entries)]


    def _get_y_values(self) -> list[float]:
        return [float(intensity) for intensity in self.intensities.get_value()]

    @classmethod
    def is_stoe(cls, fpath : str) -> bool:
        try:
            reader = StoeParser()
            reader.read(fpath=fpath)
            angle_start, angle_end = reader.angle_start.get_value(), reader.angle_end.get_value()
            num_entries = reader.num_entries.get_value()

            angles_ok = 0 < angle_start < angle_end < 180
            entries_ok = isinstance(num_entries, int) and 0 < num_entries < 10**6
            is_stoe = angles_ok and entries_ok

        except:
            is_stoe = False

        return is_stoe

