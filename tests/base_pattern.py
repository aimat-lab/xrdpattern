from xrdpattern.parsing import MasterParser
from xrdpattern.parsing.examples import DataExamples
from xrdpattern.pattern import XrdPattern
from holytools.devtools import Unittest


class ParserBaseTest(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.pattern: XrdPattern = XrdPattern.load(fpath=DataExamples.get_bruker_fpath())
        cls.parser : MasterParser = MasterParser()
        cls.pattern.save(fpath=DataExamples.get_aimat_fpath(), force_overwrite=True)

    def check_data_ok(self, two_theta_values : list[float], intensities : list[float]):
        data_view = str(two_theta_values)[:100]+ '...' +  str(two_theta_values)[-100:]
        print(f'data is {data_view}')
        for key, value in zip(two_theta_values, intensities):
            self.assertIsInstance(key, float)
            self.assertIsInstance(value, float)
