from xrdpattern.xrd_types import XrdPatternDB
import os

if __name__ == "__main__":
    submission_dir = '/home/daniel/r_mirror/pxrd/sutter_fella_1'
    data_root_path = os.path.join(submission_dir,'data')
    patterndb = XrdPatternDB(data_root_path=data_root_path)
    patterndb.export(container_dir=submission_dir)