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





