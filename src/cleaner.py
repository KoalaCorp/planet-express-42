from cucco import Cucco
import ftfy
from nltk import data
from nltk import FreqDist
from nltk import pos_tag
from nltk.tokenize import word_tokenize

from settings import TOP_WORDS


LANGUAGE = 'es'
NORMS = [
    'remove_stop_words',
    'replace_punctuation',
    'remove_extra_whitespaces',
    ('replace_characters', {'characters': ('“', '”'), 'replacement': ' '})]
tokenizer = data.load('tokenizers/punkt/spanish.pickle')


class Tokenized(object):
    def __init__(self, text):
        self.text = text

    def clean_text(self):
        lines = tokenizer.tokenize(self.text)
        norm_esp = Cucco(language=LANGUAGE)
        esp_texts = [norm_esp.normalize(sentence, NORMS) for sentence in lines]
        esp_texts = [ftfy.fix_encoding(sentence) for sentence in esp_texts]
        esp_tokens = [word_tokenize(sentence) for sentence in esp_texts]

        flat_list = []
        names = []
        name = ''
        for sentence in esp_tokens:
            for word, tag in pos_tag(sentence):
                flat_list.append(word)
                if tag == 'NNP':
                    name = '{} {}'.format(name, word)
                else:
                    if name != '':
                        name.lstrip()
                        names.append(name)
                        name = ''

        esp_freq = FreqDist(word for word in flat_list)

        return {
            'topics': [{"word": word[0], "score":word[1]}
                       for word in esp_freq.most_common()[:TOP_WORDS]],
            'names': names}
