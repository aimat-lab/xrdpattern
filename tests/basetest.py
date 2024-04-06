from xrdpattern.core import XrdIntensities
from xrdpattern.pattern import XrdPattern
from hollarek.devtools import Unittest
from abc import abstractmethod

class ParserBaseTest(Unittest):
    def check_data_ok(self, data : XrdIntensities):
        data_view = str(data)[:1000]+ '...' +  str(data)[-1000:]
        print(f'data is {data_view}')
        data_str = data.to_str()
        self.assertIsInstance(data_str, str)

        keys, values = data.as_list_pair()
        for key, value in zip(keys, values):
            self.assertIsInstance(key, float)
            self.assertIsInstance(value, float)

    @staticmethod
    def get_stoe_fpath() -> str:
        return '/home/daniel/local/misc/example_files/stoe.raw'

    @staticmethod
    def get_bruker_fpath() -> str:
        return '/home/daniel/local/misc/example_files/bruker.raw'

    @staticmethod
    def get_single_csv_fpath() -> str:
        return '/home/daniel/local/misc/example_files/single.csv'

    @staticmethod
    def get_multi_csv_fpath() -> str:
        return '/home/daniel/local/misc/example_files/multi.csv'

    @staticmethod
    def get_datafolder_fpath() -> str:
        return '/home/daniel/local/misc/example_files/datafolder'


class PatternBaseTest(ParserBaseTest):
    def setUp(self):
        self.pattern = XrdPattern.load(fpath=self.get_fpath())

    @abstractmethod
    def get_fpath(self) -> str:
        pass
