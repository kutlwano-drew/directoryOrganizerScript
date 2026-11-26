import tempfile
import unittest
from pathlib import Path
from hybrid_file_organiser.engine import build_plan, unique_destination
from hybrid_file_organiser.config import default_config

class EngineTests(unittest.TestCase):
    def test_category_plan(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            file = root / "notes.pdf"
            file.write_text("hello")
            plan, skipped = build_plan([file], root, default_config())
            self.assertEqual(len(plan), 1)
            self.assertEqual(plan[0].category, "Documents")
            self.assertEqual(len(skipped), 0)

    def test_collision_name(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "same.txt"
            path.write_text("one")
            candidate = unique_destination(path)
            self.assertEqual(candidate.name, "same (1).txt")

if __name__ == "__main__":
    unittest.main()
