from collections import defaultdict

import spacy

from settings import SPACY_CORPUS


NLP = spacy.load(SPACY_CORPUS)


class Tokenized(object):

    words_to_avoid = ("DET", "ADP", "AUX", "CCONJ", "SCONJ", "NUM", "PART",
                      "PRON", "SYM", "CONJ", "SPACE")

    def __init__(self, text):
        self.text = text

    def clean_text(self):
        doc = NLP(self.text)

        names = defaultdict(int)
        topics = defaultdict(int)
        entities = defaultdict(lambda: {"score": 0, "entity": 0})
        for token in doc:
            word = token.text
            if token.is_stop != True and token.is_punct != True:
                if token.pos_ == "NOUN":
                    names[word] += 1
                elif token.pos_ not in self.words_to_avoid:
                    topics[word] += 1

        for ent in doc.ents:
            word = ent.text
            entities[word]["score"] += 1
            entities[word]["entity"] = ent.label

        return {
            'topics': [{"word": key, "score": val}
                       for key, val in topics.items()],
            'names': [{"word": key, "score": val}
                      for key, val in names.items()],
            'entities': [{"word": key, "score": val["score"],
                          "entity": val["entity"]}
                         for key, val in entities.items()]
        }
