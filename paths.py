import os


def get_subfile_fpaths(self) -> list[str]:
    subfile_paths = []
    for root, dirs, files in os.walk(self.get_path()):
        for file in files:
            fpath = os.path.join(root, file)
            subfile_paths.append(fpath)
    return subfile_paths