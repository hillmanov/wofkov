import re
from collections import defaultdict
from collections import OrderedDict
from itertools import product
import sqlite3
import os

class WofKov(object):
    def __init__(self):
        # Initialize database connection
        self._conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.realpath(__file__)), "db.sqlite"))
        self._c = self._conn.cursor()

    def get_possibilities(self, puzzle, excluded_letters):
        letters = set(re.findall("[a-zA-Z]", puzzle + excluded_letters))
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
                trigram_results = self._c.execute("""
                    SELECT context_1, context_2, word
                    FROM trigram 
                    WHERE context_1 GLOB ?
                    AND context_2 GLOB ?
                    AND word GLOB ?
                    ORDER BY frequency DESC """, (context_1, context_2, word)).fetchall()

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
                bigram_results = self._c.execute("""
                    SELECT context, word
                    FROM bigram 
                    WHERE context GLOB ?
                    AND word GLOB ?
                    ORDER BY frequency DESC """, (context, word)).fetchall()

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
                unigram_results = self._c.execute("""
                    SELECT word
                    FROM unigram
                    WHERE word GLOB ?
                    ORDER BY frequency DESC """, (word,)).fetchall()

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
