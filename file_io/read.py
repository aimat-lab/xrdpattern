from xylib.xyconv import convert_file
import enum

from xylib.xyconv import list_supported_formats

list_supported_formats()


class Format(enum):
    pass

class XYLibOption:
    def __init__(self, input_path : str, output_path : str):
        self.INPUT_PATH : str = input_path
        self.OUTPUT_PATH : str = output_path
        self.s : bool = True


def convert(input_path : str, output_path : str, output_format : Format):
    option = XYLibOption(input_path=input_path, output_path=output_path)


    convert_file(opt=option)

