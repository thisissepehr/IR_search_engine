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
date = '2022-03-31'

# global DB variables
db_host = "localhost"
db_user="populator",
db_password="d9pifetoyesad2cekipoyolis",
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
dataset = {}
nlp = spacy.load('en_core_web_sm')
stemmer = snowballstemmer.stemmer("english")
MAX_FILE_NUMER = 1000

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
                    title = d["metadata"]["title"]
                    authors = d["metadata"]["authors"]
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

def preprocess(doc_id,token):
    strtok = ''
    if not stop_words or (token.is_alpha and not token.is_stop and len(token.orth_) > 1):
        if lemmatize:
            strtok = token.lemma_.strip() 
        elif stem:
            strtok = stemmer.stemWord(strtok)
        else:
            token.orth_.strip()
        if case_fold:
            strtok = strtok.casefold()
        return strtok                

def load_json():
    ids, texts = iter_and_parse_all_files('./'+date+'/document_parses/pdf_json/')
    docs = nlp.pipe(texts, batch_size=10)
    for paperid, doc in zip(ids, docs):
        processed_text = ''
        for token in doc:
            processed_toke = preprocess(doc_id,token)
            if processed_toke == '':
                continue
            processed_text = processed_text +' '+token
        data = dataset.get(paperid)
        data['body'] = processed_text
        dataset.update({paperid:{data}})


def load_cvs():
    global dataset
    counter = 0
    with open('./'+date+'/all_sources_metadata_'+date+'.csv') as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            doi = row['doi']
            title = row['title']
            abstract = row['abstract']
            authors = row['authors']
            publish_time = row['publish_time']
            paperid = row['pdf_json_files'][25:]
            if (not paperid == '' and not publish_time == '' and not abstract == '' and not authors == '' and not title == '' and not doi == ''):
                if(not doi.startswith('http://dx.doi.org/')): doi = 'http://dx.doi.org/'+doi
                dataset.update({paperid:{'doi': doi, 'title': title, 'abstract': abstract, 'authors': authors, 'publish_time': publish_time, 'body': ''}})
            counter = counter + 1
            if counter == MAX_FILE_NUMER:
                break

''' load_dataset function
    Loads the Dataset from file and downloads the file from server if file non existent
'''
def load_dataset():
    dl.download()
    load_cvs()
    load_json()

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
            id = populator_cursor.lastrowid()
            return id
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
        val_author = entry['authors']# TODO this string to be split to match the SQL statements
        val_paper = (entry['title'], entry['doi'], entry['abstract'], entry['publish_time'], entry['body'], len(entry['body'].split()))
        val_word = entry['body'].split()

        select_val_paper = {'idPaper': entry['id']}
        insert_val_paper = (entry['id'], entry['title'], entry['word_count'])
        paper_id = add_object_to_DB(insert_sqls['Paper'], select_sqls['Paper'], select_val_paper, insert_val_paper, populator)
        word_ids = []
        for word in val_word:
            word_ids.append(add_object_to_DB(insert_sqls['Word'], select_sqls['Word'], val_word))


# Function to count unique words in document
def count_unique(id_):
    if id_ in d_doc_unique_words_count.keys():
        d_doc_unique_words_count[id_] = d_doc_unique_words_count[id_] + 1
    else:
        d_doc_unique_words_count[id_] = 1

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