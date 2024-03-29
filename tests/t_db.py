from xrdpattern.database import PatternDB
from xrdpattern.parsing import ParserOptions
from hollarek.devtools import Unittest
import tempfile
import os, uuid


class TestPatternDB(Unittest):

    def test_save_load_roundtrip(self):
        pattern_db = PatternDB.load(datafolder_path=self.get_datafolder_fpath(), parser_options=ParserOptions(select_suffixes=['.raw']))
        tempdir_path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        pattern_db.save(path=tempdir_path)

        new_pattern_db = pattern_db.load(tempdir_path)
        oldpattern, new_patterns= pattern_db.patterns, new_pattern_db.patterns

        self.assertEqual(len(oldpattern), len(new_patterns))
        for old, new in zip(oldpattern, new_patterns):
            self.assertEqual(first=old, second=new)

    @staticmethod
    def get_datafolder_fpath() -> str:
        return '/home/daniel/local/pxrd/Simon_Schweidler_Ben_Breitung_2024_02_22/data/data_kupfer/Ben/MOF/'


if __name__ == "__main__":
    TestPatternDB.execute_all()