import os.path
from uuid import uuid4
from tempfile import TemporaryDirectory
from typing import Optional

from .xrd_types import XYLibOption, allowed_suffix_types, XrdFormat
from .xyconv import convert_file
# -------------------------------------------


def get_xy_repr(input_path : str, input_format_hint : Optional[XrdFormat] = None) -> str:
    if not os.path.isfile(input_path):
        raise ValueError(f"File {input_path} does not exist")

    if input_format_hint is None:
        input_format_suffix = input_path.split('.')[-1]
    else:
        input_format_suffix = input_format_hint.suffix
    if not input_format_suffix in allowed_suffix_types:
        raise ValueError(f"File {input_path} is not a supported format")

    try:
        with TemporaryDirectory() as output_dir:
            file_name = uuid4()
            output_path =  os.path.join(output_dir, f"{file_name}.axrd")
            option = XYLibOption(input_path=input_path, output_path=output_path, input_type = input_format_hint)
            convert_file(opt=option)
            return get_file_contents(filepath=output_path)

    except Exception as e:
        raise ValueError(f"Error obtaining xy repr of file {input_path}: {str(e)}")


def get_file_contents(filepath : str) -> str:
    if not os.path.isfile(filepath):
        raise ValueError(f"File {filepath} does not exist")

    with open(filepath, "r") as file:
        return file.read()
