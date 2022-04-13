<img src="https://people.bath.ac.uk/mtc47/img/collaborators/QM_Logo.png" height=100>

## Information Retrieval (Assignment 3): Search Engine Implementation

Module Code: **ECS736P** 

Module Leader: **Qianni Zhang**

Semester: **2**

Submission Date: **15th April 2022**

__Team Members:__
* [Alexander Sworski](mailto:a.sworski@se21.qmul.ac.uk)
* [Amir Sepehr Aminian](mailto:a.aminian@se21.qmul.ac.uk)
* [Patrick John Levermore](mailto:p.levermore@se21.qmul.ac.uk)
* [Bhavya Rajesh Makwana](mailto:b.r.makwana@se21.qmul.ac.uk)

#### Final Grade: 100%

## Overview

This project uses Python 3 and spacY and NLTK for the basic libraries and coreNLP in the map reduce example.
Indexing all the documents in python takes about 3 Hours. The map-reduce implementation only requires less time.
The searcher uses the indexes provided and can score documents based on cosine similarity in a few seconds (1000 entries ranking list).
You can score the topics based on TF-IDF, BM25 and BM25VA. The articles used in this project CORD19, a collection of all 
published scientific papers on COVID-19 from [CORD19](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases.html)

## Run requirements

Everything was built on Python 3.6 but should run on earlier versions as well.
Package requirements:

- numpy~=1.21.2
- spacy~=3.0.8
- snowballstemmer~=2.2.0
- nltk~=3.7
- mysql-connector-python~=8.0.28
- requests~=2.27.1

Please Note: From the DataSet Extract the zip and go to 2020-05-12/document_parses/pdf_json, copy files you want to index and 
past it to data/DataFiles, Indexer will only index these files

## Index

We create three different dictionaries during the indexing phase.
We run through all the documents and build the dictionaries by adding new entries.
The dictionaries are stored in pickle format, and push all required data in database.

- Inverted index with the words as keys, as values we save the docNo and the occurrence rate (see below)
- Word counter index which contains the length of all documents
- Word unique counter index which is needed for BM25VA

### Examples:

Inverted index:
{write : {doc1 : 2, doc2: 5},
zone : {doc5 : 1}}

Word counter:
{doc1 : 100}

Unique word conter:
{doc1 : 35}


The following metrics are calculated as well
- total number of documents
- total number of words in all documents

### Natural language pre-processing

Several pre-processing options are implemented an can be used via the commandline (lemmatization, stemming, stopwords removal, case folding).
They can be used in any combination apart from lemmatization and stemming together.
We use spacy for the tokenization, stopwords removal and case folding. For stemming we use snowball-stemmer.

Several *Special strings* are handled. Basic stopwords are already removed in spacy via
- default english stopwords (`en_core_web_sm.STOPWORDS`)
- spacy doesn't sort out word fragments which contain some special characters like "-", we chose to remove them with isalpha as well. It could be argued to handle these differently.
- custom stopwords
All of these are excluded from the tokens which later on are stored in the index.

Case-folding is implemented with the python string method "casefold()".

Please Note: Do the same pre-processing for documents and query(By default we are using lemmatizing and stopwords removal)

### Scoring

We have implemented *tf-idf*, *bm25* and *bm25va* scoring. The ranking works as follows:
For each word that is both in the query and in the document we calculate the score of both the query and the documents. 
We use cosine similarity for ranking, however we kind of calculate it while creating the vectors.
We add up the upper part of cosine similarity A*B for all documents if they have the word (otherwise it the product is 0).
We add up the "vector_betrag" (x²) while going through the words and documents and use sqrt on it after the loop.
Then we have another loop to connect the lower and upper part of the cosine similarity for all documents.
For each topic word we iterate over all the entries of the word in the inverted index, therefore all documents with at least one same word get scored and ranked.
In the end we sort them and only use the best 1000.

The tf-idf, bm25 and bm25va implementations are pretty straightforward and carefully put into methods to easily see how they are implemented.
One thing worth mentioning is that we implemented the term frequency as: word_occurrence / document_length (in words).
However all methods are written to be able to be easily looked up in the search.py.

It is interesting that the differences in the table below are so small. TF-IDF surely performed better because we added the document length to it, however we thought
it would still perform worse.
We were also surprised that BM25VA performed worse than BM25, it even made us check our implementation again (however everything seems correctly implemented).
We have some ideas to why this could be the case. The default "b"-value in BM25 of 0.75 is fits probably pretty well for all the documents we indexed. They articles
are "as normal as texts get" on average, so the default value should perform very well. If all the articles however were extremely long or just a few words short, than
the default b value would probably fail. With the average length of 261 words per document it fits well. In addition to that we assume that the b-calculation of BM25VA
is only "vague". That means the b-value is never completely wrong, but also not optimized. In every case the b-values could be adjusted by hand to achieve better results.
Because of this we think that BM25VA is only good if you know nothing about the texts or have completely different texts (very short and very long), which was not the case
in this assignment.

Scoring results are stored at the end in the text file as per the method selected
* scored_bm25.txt
* scores_bm25va.txt
* scores_tf-idf.txt

Format is as follows:<br />
Input Query: An Extended Outbreak of Infectious Peritonitis in a Closed Colony of European Wildcats (Fells silvestris)<br />
topicNo, score[0]'(File Name)', rank_counter, score[1] <br />
None, 0a0bc6bc993e37df9be46a2c80e969cbac5a89db, 1, 0.8668498598860553 <br />
None, 0b1515138984b9f9f2d08a8aaedc388846b531d4, 2, 0.3998634550118276 <br />
None, 0ab9753b9860f6b8c433f07e1bf96c98f452ecb1, 3, 0.39899786579916413 <br />
None, 0ba1801a150e25b029cf3c2a38573435b21dea80, 4, 0.34348281131845837 <br />

Note: All scores are from the default settings of the indexer.py - lemmatization and stopwords on.

### Evaluation of significance

### Running the project

#### Indexer
$ python indexer.py [-case | -lemm | -stem | -stop] [-none]
OR
$ python indexer.py

-case turns on case-folding.
-lemm turns on the lemmatization. Does NOT work in combination with stemming.
-stem turns on stemming. Does NOT work in combination with lemmatizing.
-stop turns on the stop word filter.
                
-none turns everything OFF and only runs with basic tokens. ignores all other args


DEFAULT SETTINGS FOR DOCUMENTS:

- case-folding OFF
- stemming OFF
- lemmatization ON
- stop word filters ON

#### Searcher

$ python search.py 

DEFAULT SETTINGS FOR QUERY:

- case-folding OFF
- stemming OFF
- lemmatization ON
- stop word filters ON

Note: You can change the query preprocessing in search.py file by setting these booleans:
* lemmatize = True
* stem = False
* stop_words = True
* case_fold = False

## Dependencies
In order to run this project you have to solve some UI dependencies and some python dependencies.

#### UI dependencies
This project runs on node.js framework. You can download it from [here](https://nodejs.org/en/). To initialize the project go to the project directory in the **www** folder (you should see a file called _package.json_) and the use the code below: 
```
npm install
```
#### Python Dependencies
```
pip install -r requirements.txt
```

## Run the Project
To run the project with UI you have to run the server on local host like this:
```
node './www/src/app.js'
```






