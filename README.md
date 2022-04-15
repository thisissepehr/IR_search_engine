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

#### Final Grade: ??%

## Overview

For this Project, a Search Engine has been developed that allows the User to search through the articles collected by [CORD19](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases.html), which is a COVID-19 reasearch paper database.


## Running the Project

### Using  Docker
The whole Project has been developed so that it can be easily executed and deployed using the single Docker command.

-  `docker-compose up`

This will create a Docker App, which will consist of two containers. One Backend Contianer, which runs the Python and Javascript code. The second contianer hosts the MySQL Database.

## Executing the Indexer
**SYNOPSIS:**
    
    python indexer.py

**DESCRIPTION**

The Indexer populates the Database with the Dataset. This operation can be very time intensive, as the most recent Dataset of the [CORD19](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases.html) collection has a size of ~80GB (April 2022). Therefore, we chose an earlier version of the collection with size 2GB, but the code would remain workable for a larger version.
We fetch three different types of data from corpus during the indexing phase. We run through all the documents and build the dataset by adding new entries. The dataset is stored in Database

Inverted index with the words as keys, as values we save the docNo and the occurrence rate (see below)
Word counter index which contains the length of all documents
Word unique counter index which is needed for BM25VA<br /><br />
Examples:<br />
Inverted index: {write : {doc1 : 2, doc2: 5}, zone : {doc5 : 1}}

Word counter: {doc1 : 100}

Unique word counter: {doc1 : 35}

The following metrics are calculated as well

* total number of documents
* total number of words in all documents

## The Methodology

### Natural language pre-processing

Several pre-processing options are implemented (lemmatization=ON, stemming=OFF, stopwords removal=ON, case folding=ON).
They can be used in any combination apart from lemmatization and stemming together.
We use spacy for the tokenization, stopwords removal and case folding. For stemming we use snowball-stemmer.

Several *Special strings* are handled. Basic stopwords are already removed in spacy via
- default english stopwords (`en_core_web_sm.STOPWORDS`)
- spacy doesn't sort out word fragments which contain some special characters like "-", we chose to remove them with isalpha as well. It could be argued to handle these differently.
- custom stopwords
All of these are excluded from the tokens which later on are stored in the index.

Case-folding is implemented with the python string method "casefold()".

### Scoring & Evaluation of significance

We have implemented *tf-idf*, *bm25*, *bm25L*, *bm25+* and *bm25va* scoring. The ranking works as follows:
For each word that is both in the query and in the document we calculate the score of both the query and the documents. 
We use cosine similarity for ranking, however we kind of calculate it while creating the vectors.
We add up the upper part of cosine similarity A*B for all documents if they have the word (otherwise it the product is 0).
We add up the "vector_betrag" (x²) while going through the words and documents and use sqrt on it after the loop.
Then we have another loop to connect the lower and upper part of the cosine similarity for all documents.
For each topic word we iterate over all the entries of the word in the inverted index, therefore all documents with at least one same word get scored and ranked.
In the end we sort them and only use the best 1000.

The tf-idf, bm25 and bm25va implementations are pretty straightforward and carefully put into methods to easily see how they are implemented.
One thing worth mentioning is that we implemented the term frequency as: word_occurrence / document_length (in words).
However, all methods are written to be able to be easily looked up in the search.py.

It is interesting that the differences in the table below are so small. TF-IDF surely performed better because we added the document length to it, however we thought
it would still perform worse.
We were also surprised that BM25VA performed worse than BM25, it even made us check our implementation again (however everything seems correctly implemented).
We have some ideas to why this could be the case. The default "b"-value in BM25 of 0.75 is fits probably pretty well for all the documents we indexed. They articles
are "as normal as texts get" on average, so the default value should perform very well. If all the articles however were extremely long or just a few words short, than
the default b value would probably fail. With the average length of 2000 words per document it fits well. In addition to that we assume that the b-calculation of BM25VA
is only "vague". That means the b-value is never completely wrong, but also not optimized. In every case the b-values could be adjusted by hand to achieve better results.
Because of this we think that BM25VA is only good if you know nothing about the texts or have completely different texts (very short and very long), which was not the case
in this assignment.

Scoring results are stored at the end in the database as per the method selected

Note: All scores are from the default settings of the indexer.py - lemmatization, case-folding and stopwords on.

 

### Roles 

Alexander Sworski: System Structure/Architecture, Database setup, retrieval/indexing model development 

Amir Sepehr Aminian: Repo Setup, Input Pre-processing, Designing user interface, Relevance Analysis 

Bhavya Makwana: Tool Analysis/research, pairing on retrieval/indexing model development, preparation/analysis of results. 

Patrick Levermore: Query processor model/framework, retrieval/indexing model development 







