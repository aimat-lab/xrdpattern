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


    @classmethod
    def get_stoe_fpath(cls) -> str:
        return cls.get_example_folderpath() + 'stoe.raw'

    @classmethod
    def get_bruker_fpath(cls) -> str:
        return cls.get_example_folderpath() + 'bruker.raw'

    @classmethod
    def get_single_csv_fpath(cls) -> str:
        return cls.get_example_folderpath() + 'single.csv'

    @classmethod
    def get_multi_csv_fpath(cls) -> str:
        return cls.get_example_folderpath() + 'multi.csv'

    @classmethod
    def get_aimat_json_fpath(cls) -> str:
        return cls.get_example_folderpath() + 'aimat.json'

    @classmethod
    def get_datafolder_fpath(cls) -> str:
        return cls.get_example_folderpath() + 'datafolder'

    @staticmethod
    def get_example_folderpath() -> str:
        return '/home/daniel/pxrd/examples/'

class PatternBaseTest(ParserBaseTest):
    @classmethod
    def setUpClass(cls):
        pattern_from_bruker = XrdPattern.load(fpath=cls.get_bruker_fpath())
        pattern_from_bruker.save(fpath=cls.get_aimat_json_fpath(), force_overwrite=True)

    def setUp(self):
        self.pattern = XrdPattern.load(fpath=self.get_fpath())

    @abstractmethod
    def get_fpath(self) -> str:
        pass
