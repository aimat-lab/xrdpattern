from xrdpattern.pattern import PatternDB

# ---------------------------------------------------------


def parse_directory(input_dirpath : str, output_dirpath : str):
    pattern_db = PatternDB.load(dirpath=input_dirpath, selected_suffixes=['.raw'])
    pattern_db.save(dirpath=output_dirpath)


if __name__ == "__main__":
    out_dirpath = '/home/daniel/Drive/data/workspace/opxrd'
    in_dirpath = '/home/daniel/Drive/data/opxrd/v0_backup/breitung_schweidler_0/data'
    parse_directory(input_dirpath=in_dirpath, output_dirpath=out_dirpath)
