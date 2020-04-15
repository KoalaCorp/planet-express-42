import json
import unittest

from cleaner import Tokenized


class TokenizedCleanTestTestCase(unittest.TestCase):
    def test_clean_text(self):
        with open('tests/cleaner_test.json') as json_file:
            json_data = json.load(json_file)
            json_data_tokenized = json_data['tokenized'][0]
            tokenized = Tokenized(json_data['content'])
            self.assertEqual(tokenized.clean_text(), {
                'topics': json_data_tokenized['topics'],
                'names': json_data_tokenized['names']})
