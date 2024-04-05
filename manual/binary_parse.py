from dataclasses import dataclass
from enum import Enum
from typing import Optional
import struct

class BlockFmt(Enum):
    PASCAL_STRING = 'p'
    FLOAT = 'f'
    DOUBLE = 'd'
    SIGNED_CHAR = 'b'
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

@dataclass
class Block:
    size : int
    data_structure : BlockFmt

    def get_fmt_str(self) -> str:
        elementary_size = self.data_structure.get_num_bytes()
        if not elementary_size is None:
            if self.size % elementary_size != 0:
                raise ValueError(f'Block size {self.size} must be multiple of size of specified '
                                 f'datastructure {elementary_size} bytes')
            num = self.size//elementary_size
        else:
            num = self.size
        return f'{num}{self.data_structure.value}'


class BinaryFormat:
    def __init__(self, block_list):
        self.block_list = block_list

    def get_fmt_str(self) -> str:
        fmt_str = ''
        for block in self.block_list:
            fmt_str += block.get_fmt_str()
        return fmt_str


    def decode(self, fpath : str) -> str:
        with open(fpath, mode='rb') as file:
            byte_content = file.read()
        return self._decode_bytes(byte_content=byte_content)


    def _decode_bytes(self, byte_content : bytes) -> str:
        the_fmt_str = self.get_fmt_str()
        print(the_fmt_str)
        unpacked_blocks = struct.unpack(the_fmt_str,  byte_content)
        plain_text = ''
        for block in unpacked_blocks:
            if isinstance(block, bytes):
                block = block.decode(encoding='utf-8')
            plain_text += str(block)
        return plain_text




if __name__ == "__main__":
    import struct

    example_tuple = (42, "Hello, World!", 3.14, 1, 2, 3, 4, 5)
    string_length = len(example_tuple[1].encode())
    fmt_str_correct = f'i{string_length}pf5i'
    packed_data_correct = struct.pack(fmt_str_correct, example_tuple[0], example_tuple[1].encode(), example_tuple[2],*example_tuple[3:])
    unpacked_data_correct = struct.unpack(fmt_str_correct, packed_data_correct)

    blocks = [
        Block(size=4, data_structure=BlockFmt.INT_OR_LONG),
        Block(size=string_length, data_structure=BlockFmt.PASCAL_STRING),
        Block(size=4, data_structure=BlockFmt.FLOAT),
        Block(size=20, data_structure=BlockFmt.INT_OR_LONG)
    ]

    bin_fmt = BinaryFormat(block_list=blocks)
    print(bin_fmt._decode_bytes(byte_content=packed_data_correct))


# if __name__ == "__main__":
#     abs8_blocks = [
#         # HEADER
#         Block(size=5, data_structure=BlockFmt.PASCAL_STRING),  # "AVS84"
#         Block(size=9, data_structure=BlockFmt.PASCAL_STRING),  # ?
#         Block(size=9, data_structure=BlockFmt.PASCAL_STRING),  # Spectrometer serial ID
#         Block(size=1, data_structure=BlockFmt.PASCAL_STRING),  # ?
#         Block(size=9, data_structure=BlockFmt.PASCAL_STRING),  # Spectrometer serial ID
#         Block(size=3, data_structure=BlockFmt.PAD_BYTE),  # null padding?
#         Block(size=292, data_structure=BlockFmt.PASCAL_STRING),  # ?
#
#         # SERIES
#         Block(size=13600, data_structure=BlockFmt.FLOAT),  # X axis
#         Block(size=13600, data_structure=BlockFmt.FLOAT),  # Y axis
#         Block(size=13600, data_structure=BlockFmt.FLOAT),  # Z axis
#
#         # FOOTER
#         Block(size=13612, data_structure=BlockFmt.PAD_BYTE),  # null padding?
#         Block(size=4, data_structure=BlockFmt.FLOAT),  # constant 1.0f
#         Block(size=5, data_structure=BlockFmt.PAD_BYTE),  # null padding?
#         Block(size=1884, data_structure=BlockFmt.FLOAT),  # constant 10.0f array?
#         Block(size=1883, data_structure=BlockFmt.PAD_BYTE),  # null padding?
#     ]
#     abs8 = BinaryFormat(block_list=abs8_blocks)
#     abs8.decode(fpath='/home/daniel/OneDrive/Downloads/SD181_1_abs.ABS8')