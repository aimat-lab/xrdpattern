#!/usr/bin/env python
from __future__ import annotations
from typing import Optional
import xylib
from .formats import XrdFormat


__version__ = xylib.xylib_get_version()


def print_supported_formats():
    n = 0
    while True:
        form = xylib.xylib_get_format(n)
        if not form:
            break
        print('%-20s: %s' % (form.name, form.desc))
        n += 1

def print_filetype_info(filetype):
    fi = xylib.xylib_get_format_by_name(filetype)
    if fi:
        print("Name: %s" % fi.name)
        print("Description: %s" % fi.desc)
        print("Possible extensions: %s" % (fi.exts or "(not specified)"))
        print("Flags: %s-file %s-block" % (
            ("binary" if fi.binary else "text"),
            ("multi" if fi.multiblock else "single")))
        print("Options: %s" % (fi.valid_options or '-'))
    else:
        print("Unknown file format.")


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


