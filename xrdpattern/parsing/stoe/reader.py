from xrdpattern.core import Metadata, PatternInfo, XrdIntensities
from .quantities import Quantity, FloatQuantity, IntegerQuantity

class BinaryReader:
    def read(self, fpath : str):
        with open(fpath, 'rb') as f:
            byte_content = f.read()
        self.read_bytes(byte_content=byte_content)

    def read_bytes(self, byte_content : bytes):
        for key, value in self.__dict__.items():
            if isinstance(value, Quantity):
                value.extract_value(byte_content)


class StoeReader(BinaryReader):
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


    def get_pattern_info(self, fpath : str) -> PatternInfo:
        self.read(fpath=fpath)
        metadata = Metadata(primary=self.primary_wavelength.get_value(),
                            secondary=self.secondary_wavelength.get_value(),
                            ratio=self.ratio.get_value())

        angle_values = self._get_x_values()
        float_intensities = self._get_y_values()
        data = {angle: intensity for angle, intensity in zip(angle_values, float_intensities)}
        intensities = XrdIntensities.angle_data(data=data)

        return PatternInfo(datafile_path=fpath, metadata=metadata, xrd_intensities=intensities)


    def _get_x_values(self) -> list[float]:
        start_value = self.angle_start.get_value()
        end_value = self.angle_end.get_value()
        num_entries = self.num_entries.get_value()
        step = (end_value - start_value) / (num_entries - 1)
        return [start_value + i * step for i in range(num_entries)]


    def _get_y_values(self) -> list[float]:
        return [float(intensity) for intensity in self.intensities.get_value()]
