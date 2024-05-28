from __future__ import annotations

from holytools.fsys import LocationManager as BaseManager

class LocationManager(BaseManager):
    @classmethod
    def icsd_dirpath(cls) -> str:
        return cls.relative_dir('icsd')

    @classmethod
    def statistics_fpath(cls) -> str:
        return cls.relative_file(f'{cls.icsd_dirpath()}/statistics.bin')

    @classmethod
    def cif_dirpath(cls) -> str:
        return cls.relative_dir(f'{cls.icsd_dirpath()}/cifs')

    @classmethod
    def train_dirpath(cls) -> str:
        return cls.relative_dir('train')

    @classmethod
    def test_dirpath(cls) -> str:
        return cls.relative_dir('test')

    @classmethod
    def rruff_dirpath(cls):
        return cls.relative_dir('rruff')

    # -------------------------------------------

    @classmethod
    def relative_dir(cls, relative_path: str) -> str:
        if not cls.is_initialized():
            cls._set_default_rootdirpath()
        return super().relative_dir(relative_path=relative_path)

    @classmethod
    def relative_file(cls, relative_path: str) -> str:
        if not cls.is_initialized():
            cls._set_default_rootdirpath()
        return super().relative_file(relative_path=relative_path)

    @classmethod
    def _set_default_rootdirpath(cls):
        cls.set_root()
        print(f'Warning: No root dir set for LocationManager. Initialized to default : {cls.get_root_dirpath()}')

    @classmethod
    def set_root(cls, root_dirpath: str = f'/home/daniel/Drive/data/workspace/'):
        return super().set_root(root_dirpath=root_dirpath)
