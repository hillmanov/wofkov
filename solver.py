from wofkov import WofKov
import random
import re

wofkov = WofKov()

def puzzlefy(words):
    words = words.lower()
    letters = list(set(re.findall("\w", words)))
    replace_letters = list(set([letter for i in range(random.randint(2, len(letters))) for letter in random.choice(letters)]))
    new_puzzle = words
    for letter in replace_letters:
        new_puzzle = new_puzzle.replace(letter, "_")
    return new_puzzle

puzzle = "j_m_ _h_ g__"
bad_letters = ""

results = wofkov.get_possibilities(puzzle, bad_letters)

for i, words in enumerate(results[:50]):
    print("{}: {}".format(i, words))

