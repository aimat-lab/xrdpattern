import os.path

from xrdpattern.parsing import Formats
from xrdpattern.pattern import XrdPattern
from holytools.devtools import Unittest
from abc import abstractmethod

class ParserBaseTest(Unittest):
    def check_data_ok(self, two_theta_values : list[float], intensities : list[float]):
        data_view = str(two_theta_values)[:100]+ '...' +  str(two_theta_values)[-100:]
        print(f'data is {data_view}')
        for key, value in zip(two_theta_values, intensities):
            self.assertIsInstance(key, float)
            self.assertIsInstance(value, float)

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
        example_dirpath = os.path.join(dirpath, 'examples')
        return example_dirpath


class PatternBaseTest(ParserBaseTest):
    @classmethod
    def setUpClass(cls):
        pattern_from_bruker = XrdPattern.load(fpath=cls.get_bruker_fpath())
        pattern_from_bruker.save(fpath=cls.get_aimat_xrdpattern_fpath(), force_overwrite=True)

    def setUp(self):
        self.pattern : XrdPattern = XrdPattern.load(fpath=self.get_fpath())

    @abstractmethod
    def get_fpath(self) -> str:
        pass
