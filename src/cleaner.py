from cucco import Cucco
import ftfy
from nltk import data
from nltk import FreqDist
from nltk.tokenize import word_tokenize

from settings import TOP_WORDS


LANGUAGE = 'es'
NORMS = [
    'remove_stop_words',
    'replace_punctuation',
    'remove_extra_whitespaces']
tokenizer = data.load('tokenizers/punkt/spanish.pickle')


class Tokenized(object):
    def __init__(self, text):
        self.text = text

    def clean_text(self):
        lines = tokenizer.tokenize(self.text)
        normEsp = Cucco(language=LANGUAGE)
        espTexts = [normEsp.normalize(sentence, NORMS) for sentence in lines]
        espTexts = [ftfy.fix_encoding(sentence) for sentence in espTexts]
        espTokens = [word_tokenize(sentence) for sentence in espTexts]
        flatList = [word for sentList in espTokens for word in sentList]
        espFreq = FreqDist(word for word in flatList)

        return [{"word": word[0], "score":word[1]}
                for word in espFreq.most_common()[:TOP_WORDS]]
