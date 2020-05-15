import json
import unittest

from cleaner import Tokenized


class TokenizedCleanTestTestCase(unittest.TestCase):
    def test_clean_text(self):
        with open('tests/cleaner_test.json') as json_file:
            json_data = json.load(json_file)
            json_data_tokenized = json_data['tokenized'][0]
            tokenized = Tokenized(json_data['content'])
            tokenized_clean_text = tokenized.clean_text()
            self.assertEqual(tokenized_clean_text['topics'],
                             json_data_tokenized['topics'])
            self.assertEqual(tokenized_clean_text['names'],
                             json_data_tokenized['names'])
            self.assertEqual(tokenized_clean_text['entities'],
                             json_data_tokenized['entities'])
