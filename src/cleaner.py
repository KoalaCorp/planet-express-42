from collections import defaultdict

import spacy

from settings import SPACY_CORPUS, TOP_WORDS


NLP = spacy.load(SPACY_CORPUS)


class Tokenized(object):

    words_to_avoid = ("DET", "ADP", "AUX", "CCONJ", "SCONJ", "NUM", "PART", "PRON", "SYM", "CONJ", "SPACE")

    def __init__(self, text):
        self.text = text

    def clean_text(self):
        doc = NLP(self.text)

        names = defaultdict(int)
        topics = defaultdict(int)
        for token in doc:
            word = token.text
            if token.is_stop != True and token.is_punct != True:
                if token.pos_ == "NOUN":
                    names[word] += 1
                elif token.pos_ not in self.words_to_avoid:
                    topics[word] += 1

        return {
            'topics': [{"word": key, "score":topics[key]}
                       for key in sorted(topics, key=topics.get, reverse=True)[:TOP_WORDS]],
            'names': [{"word": key, "score":names[key]}
                      for key in sorted(names, key=names.get, reverse=True)]
        }
