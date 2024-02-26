from xrdpattern.xrd_types import XrdPatternDB

if __name__ == "__main__":
    data_root_path = '/home/daniel/data/mirror/local/parsed/Simon_Schweidler_Ben_Breitung_2024_02_23/data/daten_gallium/Alaa/'
    patterndb = XrdPatternDB(data_root_path=data_root_path)
    patterndb.export_data_files(target_dir='/home/daniel/OneDrive/Downloads/raw_exportt')