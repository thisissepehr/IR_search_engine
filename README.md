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

For this Project a Search Engine has been developed that allows the User to search through the articles collected by [CORD19](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases.html), which is a COVID-19 reasearch paper database.


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

## The Methodology

### Natural language pre-processing

Several pre-processing options are implemented and can be used via the commandline (lemmatization, stemming, stopwords removal, case folding).
They can be used in any combination apart from lemmatization and stemming together.
We use spacy for the tokenization, stopwords removal and case folding. For stemming we use snowball-stemmer.

Several *Special strings* are handled. Basic stopwords are already removed in spacy via
- default english stopwords (`en_core_web_sm.STOPWORDS`)
- spacy doesn't sort out word fragments which contain some special characters like "-", we chose to remove them with isalpha as well. It could be argued to handle these differently.
- custom stopwords
All of these are excluded from the tokens which later on are stored in the index.

Case-folding is implemented with the python string method "casefold()".

### Scoring

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






