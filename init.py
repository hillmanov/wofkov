import os
import sqlite3
import re
from collections import defaultdict
from nltk.corpus import brown, treebank, words as words_list, abc, movie_reviews
from nltk.util import ngrams

conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.realpath(__file__)), "db.sqlite"))
c = conn.cursor()

c.executescript("""
    DROP TABLE IF EXISTS unigram;
    CREATE TABLE unigram ( 
        word      VARCHAR,
        frequency INTEGER 
    );
    DROP TABLE IF EXISTS bigram;
    CREATE TABLE bigram ( 
        context   VARCHAR,
        word      VARCHAR,
        frequency INTEGER 
    );
    DROP TABLE IF EXISTS trigram;
    CREATE TABLE trigram ( 
        context_1 VARCHAR,
        context_2 VARCHAR,
        word      VARCHAR,
        frequency INTEGER 
    );
""")

print("Building clean sentences list")
sentences = []

for source in (brown, treebank, abc, movie_reviews):
    for s in source.sents():
        sentences.append(' '.join(w.strip().lower().replace("'", "") for w in s if bool(re.search("^[a-zA-Z']+$", w.strip())) and w.strip() and w.strip() not in ("''", "'")))
    
def singles(sentences):
    for s in sentences:
        for n in ngrams(s.split(), 1):
            yield n[0]

def doubles(sentences):
    for s in sentences:
        for n in ngrams(s.split(), 2):
            yield n

def triples(sentences):
    for s in sentences:
        for n in ngrams(s.split(), 3):
            yield n

print("Building wofkov models...")

unigrams = defaultdict(int)
for w in singles(sentences):
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
        
print("Committing to the DB")
conn.commit()
print("Done!")
