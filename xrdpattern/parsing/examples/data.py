import os

from xrdpattern.parsing import Formats
from xrdpattern.pattern import XrdPattern


class DataExamples:
    @classmethod
    def get_stoe_fpath(cls) -> str:
        return os.path.join(cls.get_example_dirpath(), 'stoe.raw')

    @classmethod
    def get_bruker_fpath(cls) -> str:
        return os.path.join(cls.get_example_dirpath(), 'bruker.raw')

    @classmethod
    def get_single_csv_fpath(cls) -> str:
        return os.path.join(cls.get_example_dirpath(), 'single.csv')

    @classmethod
    def get_multi_csv_fpath(cls) -> str:
        return os.path.join(cls.get_example_dirpath(), 'multi.csv')

    @classmethod
    def get_aimat_fpath(cls) -> str:
        return os.path.join(cls.get_example_dirpath(), f'aimat.{Formats.aimat_suffix()}')

    @classmethod
    def get_datafolder_fpath(cls) -> str:
        return os.path.join(cls.get_example_dirpath(), 'datafolder')

    @staticmethod
    def get_example_dirpath() -> str:
        return os.path.dirname(__file__)



if __name__ == "__main__":
    pattern = XrdPattern.load(fpath=DataExamples.get_bruker_fpath())
    pattern.save(DataExamples.get_aimat_fpath(), force_overwrite=True)