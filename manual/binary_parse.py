from enum import Enum
from typing import Optional, Any
import struct
from abc import abstractmethod

class DataType(Enum):
    PASCAL_STRING = 'p'
    FLOAT = 'f'
    DOUBLE = 'd'
    UNSIGNED_CHAR = 'B'
    SHORT = 'h'
    UNSIGNED_SHORT = 'H'
    INT_OR_LONG = 'i'
    UNSIGNED_INT_OR_LONG = 'I'
    LONG_LONG = 'q'
    UNSIGNED_LONG_LONG = 'Q'
    CHAR = 'c'
    PAD_BYTE = 'x'
    BOOLEAN = '?'

    def get_num_bytes(self) -> Optional[int]:
        size_map = {
            'b': 1, 'B': 1, '?': 1,
            'h': 2, 'H': 2,
            'i': 4, 'I': 4, 'l': 4, 'L': 4,
            'q': 8, 'Q': 8,
            'f': 4, 'd': 8,
            'c': 1, 'x': 1,
        }
        return size_map.get(self.value, None)


class Quantity:
    def __init__(self, start : int, size : Optional[int] = None):
        self.start : int = start
        self.dtype : DataType = self.get_dtype()
        self.size : int = size if not size is None else self.dtype.get_num_bytes()
        self.value : Optional[Any] = None

    @abstractmethod
    def get_dtype(self) -> DataType:
        pass

    def get_value(self) -> Any:
        return self.value

    def extract_value(self, binary_content : bytes):
        if len(binary_content) < self.start + self.size:
            raise ValueError(f'Binary content has length {len(binary_content)} but expected at least {self.start + self.size} bytes')

        start = self.start
        end = self.start + self.size
        partial = binary_content[start:end]
        self.value =  struct.unpack(self.get_fmt_str(), partial)[0]

    def get_fmt_str(self) -> str:
        elementary_size = self.dtype.get_num_bytes()
        if not elementary_size is None:
            if self.size % elementary_size != 0:
                raise ValueError(f'Block size {self.size} must be multiple of size of specified '
                                 f'datastructure {elementary_size} bytes')
            num = self.size//elementary_size
        else:
            num = self.size
        return f'{num}{self.dtype.value}'

class FloatQuantity(Quantity):
    def get_dtype(self) -> DataType:
        return DataType.FLOAT

    def extract_value(self, binary_content : bytes) -> float:
        return super().extract_value(binary_content)

    def get_value(self) -> float:
        return self.value


class IntegerQuantity(Quantity):
    def get_dtype(self) -> DataType:
        return DataType.INT_OR_LONG

    def extract_value(self, binary_content : bytes) -> int:
        return super().extract_value(binary_content)

    def get_value(self) -> int:
        return self.value


class BooleanQuantity(Quantity):
    def get_dtype(self) -> DataType:
        return DataType.BOOLEAN

    def extract_value(self, binary_content : bytes) -> float:
        return super().extract_value(binary_content)

    def get_value(self) -> bool:
        return self.value

class BinaryReader:
    def read(self, fpath : str):
        with open(fpath, 'rb') as f:
            binary_content = f.read()
        for key, value in self.__dict__.items():
            if isinstance(value, Quantity):
                value.extract_value(binary_content)

class StoeReader(BinaryReader):
    def __init__(self):
        self.primary_wavelength : FloatQuantity = FloatQuantity(start=326)
        self.secondary_wavelength : FloatQuantity = FloatQuantity(start=322)
        self.ratio : FloatQuantity = FloatQuantity(start=384)
        self.num_entries : IntegerQuantity = IntegerQuantity(start=2082)


if __name__ == "__main__":
    binary_reader = StoeReader()
    binary_reader.read(fpath=f'/home/daniel/OneDrive/Downloads/SN_SS_17_JB-CR(III)_back_m.raw')

    for key, value in binary_reader.__dict__.items():
        if isinstance(value, Quantity):
            print(f'{key} : {value.get_value()}')


    # stoe_file =
    # with open(stoe_file, 'rb') as f:
    #     byte_content = f.read()
    # start = 0
    # for j in range(len(byte_content)):
    #     try:
    #         str_content = byte_content[start:j].decode()
    #     except:
    #         start = j
    #     if j % 2 == 0 and j + 4 < len(byte_content):
    #         next_bytes = byte_content[j:j+4]
    #         print(f'byte number {j}')
    #         print(struct.unpack('i', next_bytes)[0])
    #         print(f"as Float {struct.unpack('f', next_bytes)[0]}")