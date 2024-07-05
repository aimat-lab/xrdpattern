#!/usr/bin/env python
from __future__ import annotations
import os
from typing import Optional
from tempfile import NamedTemporaryFile
import xylib
__version__ = xylib.xylib_get_version()

import re
from xrdpattern.parsing.formats import XrdFormat
from dataclasses import dataclass
# -------------------------------------------

@dataclass
class XYLibPattern:
    fpath : str
    content : str

    def __post_init__(self):
        column_pattern = r'# column_1\tcolumn_2'
        matches = re.findall(pattern=column_pattern, string=self.content)
        if not matches:
            raise ValueError(f"Could not find header matching pattern \"{column_pattern}\" in file {self.fpath}")

        self.header_str, self.data_str = self.content.split(matches[0])

    def get_header(self) -> str:
        return self.header_str

    def get_data(self) -> str:
        return self.data_str


def get_xylib_repr(fpath : str, format_hint : XrdFormat) -> XYLibPattern:
    if not os.path.isfile(fpath):
        raise ValueError(f"File \"{fpath}\" does not exist")

    try:
        with NamedTemporaryFile(delete=False) as temp_file:
            output_path = temp_file.name
        option = XYLibOption(input_path=fpath, output_path=output_path, format_hint=format_hint)
        convert_file(opt=option)
        with open(output_path, "r") as file:
            content = file.read()
        return XYLibPattern(content=content, fpath=fpath)

    except BaseException as e:
        raise ValueError(f"Error obtaining xy repr of file {fpath}: {str(e)}")


def convert_file(opt : XYLibOption):
    if opt.INPUT_TYPE:
        d = xylib.load_file(opt.INPUT_FILE, opt.INPUT_TYPE.name)
    else:
        d = xylib.load_file(opt.INPUT_FILE)

    with open(opt.OUTPUT_PATH, 'w') as f:
        f.write('# exported by xylib from a %s file\n' % d.fi.name)
        export_metadata(f, d.meta)
        f.write('\n')
        number_of_blocks = d.get_block_count()
        for block_counter in range(number_of_blocks):
            block = d.get_block(block_counter)
            if number_of_blocks > 1 or block.get_name():
                f.write(f'\n### block #{block_counter} {block.get_name()}\n')
                export_metadata(f, block.meta)

            number_of_cols = block.get_column_count()
            # column 0 is pseudo-column with point indices, we skip it
            col_names = [block.get_column(col_counter).get_name() or ('column_%d' % col_counter)
                         for col_counter in range(1, number_of_cols+1)]
            f.write('# ' + '\t'.join(col_names) + '\n')
            number_of_rows = block.get_point_count()
            for row_counter in range(number_of_rows):
                values = ["%.6f" % block.get_column(k).get_value(row_counter)
                          for k in range(1, number_of_cols+1)]
                f.write('\t'.join(values) + '\n')

def export_metadata(f, meta):
    for i in range(meta.size()):
        key = meta.get_key(i)
        value = meta.get(key)
        f.write('# %s: %s\n' % (key, value.replace('\n', '\n#\t')))



class XYLibOption:
    def __init__(self, input_path : str, output_path : str, format_hint : Optional[XrdFormat] = None):
        self.INPUT_FILE : str = input_path
        self.OUTPUT_PATH : str = output_path
        self.INPUT_TYPE : Optional[XrdFormat] = format_hint
