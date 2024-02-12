import logging
from .xrd_types import Formats


def write_to_json(filepath : str, content : str):
    try:
        base_path = filepath.split('.')[0]
        filepath_suffix = filepath.split('.')[-1]

        if filepath_suffix != Formats.aimat_json.suffix:
            raise ValueError(f"Invalid file ending for json export")

    except:
        logging.warning(f"Invalid json export path {filepath}. Correcting to json suffix path")
        base_path = filepath
        filepath_suffix = Formats.aimat_json.suffix

    write_path = f'{base_path}.{filepath_suffix}'
    try:
        with open(write_path, 'w') as file:
            file.write(content)
    except:
        raise ValueError(f"Could not write to file {filepath}")
