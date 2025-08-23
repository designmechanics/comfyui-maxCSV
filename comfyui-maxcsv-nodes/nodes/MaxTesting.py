import unittest
import os
import csv
from unittest.mock import MagicMock, patch

# Mock the server module
import sys
sys.modules['server'] = MagicMock()

from MaxCSV_Loader_Dynamic import Max_CSV_Loader_Dynamic

class TestMaxCSVLoaderDynamic(unittest.TestCase):
    def setUp(self):
        self.loader = Max_CSV_Loader_Dynamic()
        self.csv_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'csv'))
        os.makedirs(self.csv_dir, exist_ok=True)
        self.csv_file = os.path.join(self.csv_dir, 'test.csv')
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['header1', 'header2', 'prompt'])
            writer.writerow(['value1', 'value2', 'test_prompt'])

    def tearDown(self):
        os.remove(self.csv_file)

    def test_browse_csv(self):
        result = self.loader.browse_csv('test.csv')
        self.assertIn('ui', result)
        self.assertIn('string_table', result['ui'])
        self.assertEqual(len(result['ui']['string_table']), 2)
        self.assertEqual(result['ui']['string_table'][0], ['header1', 'header2', 'prompt'])
        self.assertEqual(result['ui']['string_table'][1], ['value1', 'value2', 'test_prompt'])

        self.assertIn('result', result)
        self.assertEqual(len(result['result']), 10)
        self.assertEqual(result['result'][0], 'value1')
        self.assertEqual(result['result'][1], 'value2')
        self.assertEqual(result['result'][8], 1)
        self.assertEqual(result['result'][9], 'test_prompt')

if __name__ == '__main__':
    unittest.main()
