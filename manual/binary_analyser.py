from dataclasses import dataclass
from typing import Optional

# region should work such that the_list[reg.start, reg.end] yield the specified portion of the list
@dataclass
class Region:
    start : Optional[int]
    end : Optional[int]

    def __post_init__(self):
        if self.start == self.end:
            raise ValueError(f'Region start and end must be different; Got {self.start} and {self.end} respectively')

def get_zero_regions(byte_content: bytes, min_size: int = 16) -> list[Region]:
    zero_regions = []
    current_zeros = 0
    current_region_start = None

    for index, byte in enumerate(byte_content):
        if byte == 0:
            if current_region_start is None:
                current_region_start = index
            current_zeros += 1
        else:
            if current_zeros >= min_size:
                zero_regions.append(Region(start=current_region_start, end=index))
            current_zeros = 0
            current_region_start = None

    if current_zeros >= min_size:
        zero_regions.append(Region(start=current_region_start, end=len(byte_content)))

    return zero_regions


def get_complement_regions(byte_content : bytes, regions : list[Region]) -> list[Region]:
    complement_regions = []
    regions.sort(key=lambda region : region.start)

    dummy_start = Region(start=None, end=0)
    dummy_end = Region(start=len(byte_content), end=None)

    def full_regions():
        current = dummy_start
        for the_region in regions:
            yield current, the_region
            current = the_region
        yield current, dummy_end

    for prev_reg, next_reg in full_regions():
        start, end = prev_reg.end, next_reg.start
        if start != end:
            complement_regions.append(Region(start=start, end=end))

    return complement_regions



if __name__ == "__main__":
    test_bytes_1 = bytes([0]*20)
    test_bytes_2 = bytes([0]*15 + [1] + [0]*17 + [1])
    test_bytes_3 = bytes([1]*100)
    test_bytes_4 = bytes([0]*10 + [1]*5 + [0]*18 + [1] + [0]*15)

    the_test = test_bytes_4

    zero_regs = get_zero_regions(the_test, min_size=2)
    print(f'Zero regions are {zero_regs}')

    for reg in zero_regs:
        print(f'Zero region content is {the_test[reg.start:reg.end]}')

    complement_regs = get_complement_regions(the_test, zero_regs)
    print(f'Complement regions are {complement_regs}')

    for reg in complement_regs:
        print(f'Complement region content is {the_test[reg.start:reg.end]}')
