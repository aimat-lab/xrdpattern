from xrdpattern.xrd_types import XrdPatternDB

if __name__ == "__main__":
    data_root_path = '/home/daniel/r_mirror/pxrd/John_Doe_2024_02_27_2/data'
    patterndb = XrdPatternDB(data_root_path=data_root_path)
    patterndb.export(target_dir='/home/daniel/OneDrive/Downloads/raw_exportt')