import tempfile
import os, uuid
from tests.base_tests import ParserBaseTest
from xrdpattern.parsing import DataExamples
from xrdpattern.pattern import PatternDB


# ---------------------------------------------------------

class TestPatternDB(ParserBaseTest):
    def test_save_load_roundtrip(self):
        pattern_db = PatternDB.load(dirpath=DataExamples.get_datafolder_fpath(), selected_suffixes=['.raw'])
        tempdir_path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        pattern_db.save(dirpath=tempdir_path)

        new_pattern_db = pattern_db.load(tempdir_path)
        oldpattern, new_patterns= pattern_db.patterns, new_pattern_db.patterns

        self.assertEqual(len(oldpattern), len(new_patterns))

        old_pattern_map = {pattern.get_name(): pattern for pattern in oldpattern}
        new_pattern_map = {pattern.get_name(): pattern for pattern in new_patterns}

        print(f'Old patterns {old_pattern_map.keys()}')
        print(f'New patterns {new_pattern_map.keys()}')

        for pattern_name in old_pattern_map:
            old_pattern = old_pattern_map[pattern_name]
            new_pattern = new_pattern_map.get(pattern_name)
            self.assertIsNotNone(new_pattern)
            self.assertEqual(old_pattern, new_pattern)


if __name__ == "__main__":
    TestPatternDB.execute_all()