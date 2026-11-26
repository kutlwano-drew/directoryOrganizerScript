import tempfile
import unittest
from pathlib import Path
from hybrid_file_organiser.intelligence import parse_search_query, search_matches


class SearchFilterTests(unittest.TestCase):
    def test_parse_combined_filters(self):
        filters = parse_search_query('ext:pdf size:>5mb modified:30d name:invoice')
        self.assertEqual(filters['ext'], 'pdf')
        self.assertEqual(filters['size'], '>5mb')
        self.assertEqual(filters['modified_days'], 30)
        self.assertEqual(filters['name'], 'invoice')

    def test_extension_and_name_filter(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'invoice.pdf'
            file.write_bytes(b'abc')
            filters = parse_search_query('ext:pdf name:invoice')
            self.assertTrue(search_matches(file, filters))
            self.assertFalse(search_matches(file, parse_search_query('ext:doc')))

if __name__ == '__main__':
    unittest.main()
