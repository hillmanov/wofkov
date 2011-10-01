import os
import sqlite3
import re
from collections import defaultdict
from nltk.corpus import brown, treebank, words as words_list, abc, movie_reviews, genesis

conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.realpath(__file__)), "wofkov_db.sqlite"))
c = conn.cursor()

with open('wofkov_db_schema.sql', 'r') as sql:
    commands = sql.read().split(';')
    for command in commands:
        c.execute(command)
    
print "Building clean words list..."
words = [w.lower() for w in brown.words() if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")]
words.extend([w.lower() for w in treebank.words() if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")])
words.extend([w.lower() for w in words_list.words() if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")])
words.extend([w.lower() for w in abc.words() if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")])
words.extend([w.lower() for w in movie_reviews.words() if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")])
words.extend([w.lower() for w in genesis.words() if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")])

print "Building clean sentences list"
sentences = []
for s in brown.sents():
    sentences.append(' '.join(w.lower() for w in s if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")))
for s in treebank.sents():
    sentences.append(' '.join(w.lower() for w in s if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")))
for s in abc.sents():
    sentences.append(' '.join(w.lower() for w in s if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")))
for s in movie_reviews.sents():
    sentences.append(' '.join(w.lower() for w in s if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")))
for s in genesis.sents():
    sentences.append(' '.join(w.lower() for w in s if re.match("[a-zA-Z'-]+", w.strip()) and w.strip() not in ("''", "'")))

    
def singles(words):
        if len(words) < 1:
            return
        for w in words:
            if re.match("[a-zA-Z'-]+", w) and w.strip() != "''":
                yield w

def doubles(sentences):
    for s in sentences:
        s = s.split(' ')
        if len(s) < 2:
            continue
        for i in range(len(s) - 1):
                yield (s[i], s[i + 1])

def triples(sentences):
    for s in sentences:
        s = s.split(' ')
        if len(s) < 3:
            continue
        for i in range(len(s) - 3):
            yield (s[i], s[i + 1], s[i + 2])    
    
print "Building wofkov models..."
unigrams = defaultdict(int)
for w in singles(words):
    unigrams[w] += 1

bigrams = defaultdict(int)
for w1, w2 in doubles(sentences):
    bigrams[':'.join([w1, w2])] += 1

trigrams = defaultdict(int)
for w1, w2, w3 in triples(sentences):
    trigrams[':'.join([w1, w2, w3])] += 1

for word, frequency in unigrams.items():
    try:
        c.execute("""INSERT INTO unigram (word, frequency) VALUES ("{}", "{}")""".format(word, frequency))
    except:
        pass
   
for context_word, frequency in bigrams.items():
    try:
        context, word = context_word.split(":")
        c.execute("""INSERT INTO bigram (context, word, frequency) VALUES ("{}", "{}", "{}")""".format(context, word, frequency))
    except:
        pass
        
for contexts_word, frequency in trigrams.items():
    try:
        context_1, context_2, word = contexts_word.split(":")
        c.execute("""INSERT INTO trigram (context_1, context_2, word, frequency) VALUES ("{}", "{}", "{}", "{}")""".format(context_1, context_2, word, frequency))
    except:
        pass
        
print "Committing to the DB"
conn.commit()
print "Done!"