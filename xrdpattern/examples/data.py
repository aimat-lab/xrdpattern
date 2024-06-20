import os

from xrdpattern.parsing import Formats


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
    def get_aimat_xrdpattern_fpath(cls) -> str:
        return os.path.join(cls.get_example_dirpath(), f'aimat.{Formats.xrdpattern.suffix}')

    @classmethod
    def get_datafolder_fpath(cls) -> str:
        return os.path.join(cls.get_example_dirpath(), 'datafolder')

    @staticmethod
    def get_example_dirpath() -> str:
        dirpath = os.path.dirname(__file__)
        xrd_examples_dirpath = os.path.join(dirpath, 'xrd_data')
        return xrd_examples_dirpath
