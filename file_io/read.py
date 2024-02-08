import os.path
from uuid import uuid4
from tempfile import TemporaryDirectory

from .xrd_types import XYLibOption, file_endings
from .xyconv import convert_file
from .xyconv import list_supported_formats
# -------------------------------------------


def get_axrd_repr(input_path : str) -> str:
    if not os.path.isfile(input_path):
        raise ValueError(f"File {input_path} does not exist")

    input_format = '.' + input_path.split('.')[-1]
    if not input_format in file_endings:
        raise ValueError(f"File {input_path} is not a supported format")

    try:
        with TemporaryDirectory() as output_dir:
            file_name = uuid4()
            output_path =  os.path.join(output_dir, f"{file_name}.axrd")
            option = XYLibOption(input_path=input_path, output_path=output_path)
            convert_file(opt=option)
            return get_file_contents(filepath=output_path)

    except Exception as e:
        raise ValueError(f"Error obtaining xy repr of file {input_path}: {str(e)}")


def get_file_contents(filepath : str) -> str:
    if not os.path.isfile(filepath):
        raise ValueError(f"File {filepath} does not exist")

    with open(filepath, "r") as file:
        return file.read()


if __name__ == "__main__":
    list_supported_formats()