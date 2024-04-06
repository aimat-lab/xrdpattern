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
        self.num_entries.extract_value(byte_content=byte_content)
        self.intensities.size = self.num_entries.get_value()
        super().read_bytes(byte_content=byte_content)
    #
    # def get_pattern_info(self, fpath : str) -> PatternInfo:
    #     self.read(fpath=fpath)
    #     metadata = Metadata.from_wavelength(primary_wavelength=self)
    #
    #     PatternInfo(datafile_path=fpath, )
