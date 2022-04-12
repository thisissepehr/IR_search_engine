<img src="https://people.bath.ac.uk/mtc47/img/collaborators/QM_Logo.png" height=100>

## Information Retrival (Assignment 3): 
# Search Engine

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
Indexing all the documents in python takes about 3 Hours. The map-reduce implementation only requires 12 minutes.
The searcher uses the indexes provided and can score documents based on cosine similarity in a few seconds (1000 entries ranking list).
You can score the topics based on TF-IDF, BM25 and BM25VA. The articles used in this project CORD19, a collection of all 
published scientific papers on COVID-19 from [CORD19](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases.html)


## Task
A simple search engine on a Covid research papers dataset to help people get informed better!

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






