from xrdpattern.core import XrdData
from xrdpattern.pattern import XrdPattern
from xrdpattern.database import PatternDB
from xrdpattern.parsing import Parser
from hollarek.devtools import Unittest
from abc import abstractmethod

class PatternBaseTest(Unittest):
    def setUp(self):
        self.pattern = XrdPattern.load(fpath=self.get_fpath())

    @abstractmethod
    def get_fpath(self) -> str:
        pass

    def check_data_ok(self, data : XrdData):
        data_view = str(data)[:1000]+ '...' +  str(data)[-1000:]
        print(f'data is {data_view}')
        data_str = data.to_str()
        self.assertIsInstance(data_str, str)

        keys, values = data.as_list_pair()
        for key, value in zip(keys, values):
            self.assertIsInstance(key, float)
            self.assertIsInstance(value, float)

        if self.is_manual_mode:
            self.pattern.plot()
