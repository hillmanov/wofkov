import re
from dal import *
from collections import defaultdict
from collections import OrderedDict
from itertools import product
#from nltk.corpus import brown, treebank, words as words_list

class WofKov(object):
    def __init__(self, open_file):
        self._db = DAL("sqlite://wofkov_db.sqlite", migrate = False)
        self._db.define_table('unigram', Field('word'), Field('frequency', 'integer'))
        self._db.define_table('bigram', Field('context'), Field('word'), Field('frequency', 'integer'))
        self._db.define_table('trigram', Field('context_1'), Field('context_2'), Field('word'), Field('frequency', 'integer'))
        #self._init_database()

    def _singles(self, words):
        if len(words) < 1:
            return
        for w in words:
            if re.match("[a-zA-Z'-]+", w) and w.strip() != "''":
                yield w

    def _doubles(self, sentences):
        for s in sentences:
            s = s.split(' ')
            if len(s) < 2:
                continue
            for i in range(len(s) - 1):
                    yield (s[i], s[i + 1])

    def _triples(self, sentences):
        for s in sentences:
            s = s.split(' ')
            if len(s) < 3:
                continue
            for i in range(len(s) - 3):
                yield (s[i], s[i + 1], s[i + 2])

    def get_possibilities(self, puzzle, bad_letters):
        letters = set(re.findall("[a-zA-Z]", puzzle + bad_letters))
        glob_friendly_puzzle = puzzle.replace("_", "[^" + ''.join(letters) + "]")
        glob_friendly_parts = glob_friendly_puzzle.split()
        num_words = len(puzzle.split())

        index = 0
        possiblilites = []
        skip_trigram, skip_bigram = False, False
        results = defaultdict(list)
        while True:
            if index == num_words:
                words = defaultdict(OrderedDict)
                for index, result in results.items():
                    for list_of_word_lists in result:
                        for word_list in list_of_word_lists:
                            for i, word in enumerate(word_list):
                                words[index + i][word] = None

                final_list = [l.keys() for l in words.values()]
                return_list = []
                for i, word_combo in enumerate(product(*final_list)):
                    return_list.append(' '.join(word_combo))

                return return_list

            # First, try the trigram...
            if index + 3 <= num_words and not skip_trigram:
                context_1, context_2, word = glob_friendly_parts[index:index + 3]
                trigram_results = self._db.executesql("""
                    SELECT context_1, context_2, word
                    FROM trigram 
                    WHERE context_1 GLOB "{}"
                    AND context_2 GLOB "{}"
                    AND word GLOB "{}"
                    ORDER BY frequency DESC """.format(context_1, context_2, word))

                if len(trigram_results) > 0:
                    results[index].append(trigram_results)
                    index += 1
                    skip_trigram = False
                    skip_bigram = False
                    continue
                else:
                    skip_trigram = True
                    continue
            elif index + 2 <= num_words and not skip_bigram:
                # Try the bigram
                context, word = glob_friendly_parts[index:index + 2]
                bigram_results = self._db.executesql("""
                    SELECT context, word
                    FROM bigram 
                    WHERE context GLOB "{}"
                    AND word GLOB "{}"
                    ORDER BY frequency DESC """.format(context, word))
                if len(bigram_results) > 0:
                    results[index].append(bigram_results)
                    index += 1
                    skip_trigram = False
                    skip_bigram = False
                    continue
                else:
                    skip_bigram = True
                    continue
            elif index + 1 <= num_words:
                word = glob_friendly_parts[index]
                unigram_results = self._db.executesql("""
                    SELECT word
                    FROM unigram
                    WHERE word GLOB "{}"
                    ORDER BY frequency DESC """.format(word))
                if len(unigram_results) > 0:
                    results[index].append(unigram_results)
                    index += 1
                    skip_trigram = False
                    skip_bigram = False
                    continue
                else:
                    skip_trigram = False
                    skip_bigram = False
                    index += 1
                    continue
            skip_trigram = False
            skip_bigram = False

    def _init_database(self):

        print "Building clean words list..."
        words = [w.lower() for w in brown.words() if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")]
        words.extend([w.lower() for w in treebank.words() if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")])
        words.extend([w.lower() for w in words_list.words() if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")])

        print "Building clean sentences list"
        sentences = []
        for s in brown.sents():
            sentences.append(' '.join(w.lower() for w in s if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")))

        for s in treebank.sents():
            sentences.append(' '.join(w.lower() for w in s if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")))

        print "Building wofkov models..."
        unigrams = defaultdict(int)
        for w in self._singles(words):
            unigrams[w] += 1

        bigrams = defaultdict(int)
        for w1, w2 in self._doubles(sentences):
            bigrams[':'.join([w1, w2])] += 1

        trigrams = defaultdict(int)
        for w1, w2, w3 in self._triples(sentences):
            trigrams[':'.join([w1, w2, w3])] += 1

        for word, frequency in unigrams.items():
            self._db.unigram.insert(word = word, frequency = frequency)

        for context_word, frequency in bigrams.items():
           context, word = context_word.split(":")
           self._db.bigram.insert(context = context, word = word, frequency = frequency)

        for contexts_word, frequency in trigrams.items():
           context_1, context_2, word = contexts_word.split(":")
           self._db.trigram.insert(context_1 = context_1, context_2 = context_2, word = word, frequency = frequency)

        print "Committing to the DB"
        self._db.commit()
        print "Done!"
