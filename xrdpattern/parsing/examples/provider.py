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
    def get_vertical_csv_fpath(cls) -> str:
        return os.path.join(cls.get_example_dirpath(), 'vertical.csv')

    @classmethod
    def get_horizontal_fpath(cls) -> str:
        return os.path.join(cls.get_example_dirpath(), 'horizontal.csv')

    @classmethod
    def get_aimat_fpath(cls) -> str:
        return os.path.join(cls.get_example_dirpath(), f'aimat.{Formats.aimat_suffix()}')

    @classmethod
    def get_cif_fpath(cls) -> str:
        return os.path.join(cls.get_example_dirpath(), 'data.cif')

    @classmethod
    def get_xlsx_fpath(cls) -> str:
        return os.path.join(cls.get_example_dirpath(), 'vertical.xlsx')

    @classmethod
    def get_dat_fpath(cls) -> str:
        return os.path.join(cls.get_example_dirpath(), 'data.dat')

    @classmethod
    def get_datafolder_fpath(cls) -> str:
        return os.path.join(cls.get_example_dirpath())

    @staticmethod
    def get_example_dirpath() -> str:
        return os.path.dirname(__file__)
