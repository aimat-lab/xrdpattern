# import os

# from server import XRDServer
# from submit import Submission
# from locations import PathProvider, setup_local_env
# from xrdpattern.xrd_file_io import FormatSelector

# ---------------------------------------------------------
#
# setup_local_env()
# testServer = XRDServer()

#
# def parse_all():
#     storage_path = PathProvider().get_storage_path(backup=False)
#     print(storage_path)
#     dir_paths = [os.path.join(storage_path, name) for name in  os.listdir(path=storage_path)]
#
#     for path in dir_paths:
#         parse_directory(dir_path=path)

#
# def parse_directory(dir_path : str):
#     print(f'-> Processing directory {dir_path}')
#     new_submission = Submission(src_data=dir_path)
#     target_dir = PathProvider().get_storage_path(is_raw_data=False, backup=True)
#     new_submission.write_parsed_dir(target_dir_path=target_dir)
#
#
# if __name__ == "__main__":
#     parse_directory(dir_path='/home/daniel/data/mirror/local/raw/Simon_Schweidler_Ben_Breitung_2024_01_31')
