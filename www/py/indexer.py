import csv
import mysql.connector
import downloader as dl
import itertools
import os
import sys
import spacy
import json
import pickle
import snowballstemmer

# The Date identifier of the dataset that should be used
date = '2020-03-13'
# Change it to your relative path
# directory_path = "../data/10kFiles"
directory_path = "../data/DataFiles"

# global DB variables
db_host = "localhost"
db_user = "root"
db_password = "SED_Group10"
db_database = "BASP"
insert_sqls = {'Author': 'INSERT INTO Author (FirstName, LastName) VALUES (%s, %s)',
               'Paper': 'INSERT INTO Paper (idPaper, title, word_count) VALUES (%s, %s, %s)',
               'Word': 'INSERT INTO Word (word) VALUES (%s)'}
select_sqls = {'Author': 'SELECT * FROM Author WHERE FirstName = %(FirstName)s AND LastName =  %(LastName)s',
               'Paper': 'SELECT * FROM Paper WHERE idPaper = %(idPaper)s',
               'paper_to_author': 'SELECT * FROM paper_to_author WHERE fk_paper_id = %(fk_paper_id)s AND fk_author_id = %(fk_author_id)s',
               'Word': 'SELECT * FROM Word WHERE word = %(word)s',
               'word_to_paper': 'SELECT * FROM word_to_paper WHERE fk_word_id = %(fk_word_id)s AND fk_paper_id = %(fk_paper_id)s'}

# global variables
dataset = []
numer_of_files = 1
nlp = spacy.load('en_core_web_sm')
stemmer = snowballstemmer.stemmer("english")
d = {}
d_doc_words_count = {}
d_doc_unique_words_count = {}

''' load_dataset function
    Loads the Dataset from file and downloads the file from server if file non existent
'''
def load_dataset():
    gen1, gen2 = itertools.tee(iter_and_parse_all_files(directory_path))
    ids = (id_ for (id_, text) in gen1)
    texts = (text for (id_, text) in gen2)
    # docs = nlp.pipe(texts, n_process=4, batch_size=100)
    docs = nlp.pipe(texts, batch_size=10)
    file_counter = 0
    word_counter = 0

    for id_, doc in zip(ids, docs):
        doc_word_counter = 0
        file_counter += 1
        for token in doc:
            # filter out stopwords
            if not stop_words or (token.is_alpha and not token.is_stop and len(token.orth_) > 1):
                doc_word_counter = doc_word_counter + 1
                # take processed lemma or original depending on settings
                strtok = token.lemma_.strip() if lemmatize else token.orth_.strip()
                if case_fold:
                    strtok = strtok.casefold()
                if stem:
                    strtok = stemmer.stemWord(strtok)
                if strtok not in d.keys():
                    count_unique(id_)
                    d[strtok] = {id_: 1}
                elif strtok in d.keys():
                    # either increase counter or add document
                    if id_ in d[strtok].keys():
                        d[strtok][id_] = d[strtok][id_] + 1
                    else:
                        count_unique(id_)
                        d[strtok][id_] = 1
        # take only first k items to test
        # if file_counter == 1:
        #     break
        record = None
        for dicti in dataset:
            if dicti["id"] == id_:
                record = dicti
                break
        record['word_count'] = str(doc_word_counter)
        word_counter = word_counter + doc_word_counter
        d_doc_words_count[id_] = doc_word_counter

    d_doc_words_count["word_counter"] = word_counter # Stores total word counts in all files
    d_doc_words_count["doc_counter"] = file_counter # Stores total document counts

''' connect_to_DB function
    Connect to the database
'''
def connect_to_DB():
    global db_host
    global db_user
    global db_password
    global db_database
    try:
        populator = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_database
        )
        return populator
    except BaseException as err:
        print(err)
        exit(1)

''' add_object_to_DB function
    Adds a Object to the DB
    
    @param insert_sqls
        the SQL insert statement needed to add this object
    @param select_sql
        the SQL select statement needed check if it already exists and retrieve in case it dose
    @param val
        the object attributes
    
    @return
        the object id
'''
def add_object_to_DB(insert_sqls, select_sql, select_val, insert_val, populator) -> int:
    try:
        populator_cursor = populator.cursor()
        populator_cursor.execute(select_sql, select_val)
        id = populator_cursor.fetchone()
        if id is None:
            populator_cursor.execute(insert_sqls, insert_val)
            populator.commit()
            # id = populator_cursor.lastrowid()
        else:
            return id
    except BaseException as err:
        print(err)
        exit(1)

''' index function
    All the indexing happens here
'''
def index(paper_id, author_id, word_ids):
    populator_cursor = populator.cursor()
    populator_cursor.execute(insert_sqls['paper_to_author'], (paper_id, author_id))
    populator.commit()
    for word_id in word_ids:
        populator_cursor.execute(insert_sqls['word_to_paper'], (word_id, paper_id))
        populator.commit()

''' populate function
    Populates the Database
'''
def populate(populator):
    for entry in dataset:
        for auth in entry['authors']:
            first = auth["first"]
            last = auth["last"]
            select_val_author = {'FirstName': first, 'LastName': last}
            insert_val_author = (first, last)
            author_id = add_object_to_DB(insert_sqls['Author'], select_sqls['Author'], select_val_author, insert_val_author, populator)

        select_val_paper = {'idPaper': entry['id']}
        insert_val_paper = (entry['id'], entry['title'], entry['word_count'])
        paper_id = add_object_to_DB(insert_sqls['Paper'], select_sqls['Paper'], select_val_paper, insert_val_paper, populator)
        # val_word = entry['body'].split()
        word_ids = []
        # for word in val_word:
        #     word_ids.append(add_object_to_DB(insert_sqls['Word'], select_sqls['Word'], val_word, populator))

        # index(paper_id, author_id, word_ids)

# Function to count unique words in document
def count_unique(id_):
    if id_ in d_doc_unique_words_count.keys():
        d_doc_unique_words_count[id_] = d_doc_unique_words_count[id_] + 1
    else:
        d_doc_unique_words_count[id_] = 1

# Function to iterate over dataset and parse the files
def iter_and_parse_all_files(p):
    for root, dirs, files in os.walk(p):
        for file in files:
            if not file.startswith('.'):
                print('using: ' + str(os.path.join(root, file)))
                path = os.path.join(root, file)
                with open(path) as f:
                    text_only = ''
                    d = json.load(f)
                    paperid = d["paper_id"].strip()
                    metadata = d["metadata"]
                    title = metadata["title"]
                    authors = metadata["authors"]
                    abstracts = d["abstract"]
                    texts = d["body_text"]
                    dataset.append({'id': paperid, 'doi': '', 'title': title, 'abstract': '', 'authors': authors,
                                    'publish_time': '', 'body': '', 'word_count': ''})
                    for items in texts:
                        if len(str(items["text"])) != 0:
                            text_only += str(items["text"])
                    for items in abstracts:
                        if len(str(items["text"])) != 0:
                            text_only += str(items["text"])
                    for items in authors:
                        if len(str(items["first"])) != 0 or len(str(items["last"])) != 0:
                            text_only += str(items["first"]) + " " + str(items["first"])
                    text_only += title
                    yield paperid, text_only

if __name__ == "__main__":
    ############################### command line arguments, all are ON by DEFAULT #####################################
    lemmatize = False
    stop_words = False
    stem = False
    case_fold = False
    sys.argv.pop(0)
    if len(sys.argv) == 0:
        lemmatize = True
        stem = False
        stop_words = True
        print("""Using default settings:
    - case-folding OFF
    - stemming OFF
    - lemmatization ON
    - stop word filters ON
        """)
    else:
        for argu in sys.argv:
            if argu == "-none":
                lemmatize = False
                stop_words = False
                stem = False
                case_fold = False
            elif argu == "-lemm":
                if stem:
                    print("Stemming and lemmatization do not work in combination.")
                    print("Program is exiting.")
                    sys.exit(1)
                lemmatize = True
            elif argu == "-stop":
                stop_words = True
            elif argu == "-stem":
                if lemmatize:
                    print("Stemming and lemmatization do not work in combination.")
                    print("Program is exiting.")
                    sys.exit(1)
                stem = True
            elif argu == "-case":
                case_fold = True
            else:
                print("The argument {0} is not valid.".format(argu))
                print("""-case turns on case-folding.
    -lemm turns on the lemmatization. Does NOT work in combination with stemming.
    -stem turns on stemming. Does NOT work in combination with lemmatizing.
    -stop turns on the stop word filter.

    -none turns everything OFF and only runs with basic tokens. ignores all other args
    Program is exiting.""")
                sys.exit(1)

    print("Using {} as a path for files to index. Changeable in the beginning of the script.".format(directory_path))
    print('\n')
    ####################################################################################################

    load_dataset()
    populator = connect_to_DB()
    populate(populator)

    # Creates 3 Files
    # 1. Document Word Count (Word counter: {doc1 : 100})
    pickle.dump(d_doc_words_count, open("word_count.p", "wb"))
    # 2. Inverted Index (Inverted index: {write : {doc1 : 2, doc2: 5}, zone : {doc5 : 1}})
    pickle.dump(d, open("inv_ind.p", "wb"))
    # 3. Unique Word Counter (Unique word counter: {doc1 : 35})
    pickle.dump(d_doc_unique_words_count, open("unique_words_count.p", "wb"))