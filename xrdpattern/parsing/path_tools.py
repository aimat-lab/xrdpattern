import os
from typing import Optional

from pathvalidate import sanitize_filename


class PathTools:
    @staticmethod
    def to_valid_filename(name: str) -> str:
        name = name.strip()
        name = name.replace(' ', '_')
        name = sanitize_filename(name)

        return name

    @staticmethod
    def increment_idx_until_free(initial_dirpath: str) -> str:
        idx = 0
        dirpath = initial_dirpath
        while os.path.isdir(dirpath):
            idx += 1
            dirpath = f'{initial_dirpath}_{idx}'
        return dirpath

    @staticmethod
    def prune_suffix(fpath: str) -> str:
        parts = fpath.split('.')
        if len(parts) > 1:
            return '.'.join(parts[:-1])
        else:
            return fpath

    @staticmethod
    def ensure_suffix(fpath: str, suffix: str) -> str:
        parts = fpath.split('.')
        if len(parts) < 2:
            fpath = f'{fpath}.{suffix}'
        elif parts[-1] != f'.{suffix}':
            fpath = f'{parts[0]}.{suffix}'
        return fpath

    @staticmethod
    def get_suffix(fpath: str) -> Optional[str]:
        parts = fpath.split('.')
        if len(parts) > 1:
            return parts[-1]
        else:
            return None
    @staticmethod
    def get_subfile_fpaths(dirpath : str) -> list[str]:
        subfile_paths = []
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                fpath = os.path.join(root, file)
                subfile_paths.append(fpath)
        return subfile_paths