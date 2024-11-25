import os

from xrdpattern.pattern import PatternDB

# ---------------------------------------------------------


def parse_directory(input_dirpath : str, output_dirpath : str):
    pattern_db = PatternDB.load(dirpath=input_dirpath, selected_suffixes=['.raw'])
    pattern_db.save(dirpath=output_dirpath)


if __name__ == "__main__":
    opxrd_root_dirpath = '/home/daniel/aimat/opXRD/'
    in_dirpath = os.path.join(opxrd_root_dirpath, 'breitung_schweidler_0')
    out_dirpath = os.path.join()

    parse_directory(input_dirpath=in_dirpath, output_dirpath=out_dirpath)
