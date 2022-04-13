import csv
import mysql.connector
import downloader as dl
import itertools
import sys
import spacy
import json
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
populator = None
populator_cursor = None
nlp = spacy.load('en_core_web_sm')
stemmer = snowballstemmer.stemmer("english")
MAX_FILE_NUMER = 1000

# Function to iterate over dataset and parse the files
def iterate_jsons():
    for paperid,data in dataset.items():
        with open('./cord/'+date+'/document_parses/pdf_json/'+paperid) as f:
            text_only = ''
            json_data = json.load(f)
            authors = json_data["metadata"]["authors"]
            texts = json_data["body_text"]
            for items in texts:
                text_only = text_only + str(items["text"]) if len(str(items["text"])) != 0 else text_only
            data = dataset.get(paperid)
            data['authors'] = authors
            dataset.update({paperid:{data}})
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

def parse_json():
    paperids, texts = itertools.tee(iterate_jsons())
    paperids = (id_ for (id_, text) in paperids)
    texts = (text for (id_, text) in texts)
    texts = nlp.pipe(text, batch_size=10)
    for paperid, text in zip(paperids, texts):
        text = nlp.pipe(text, batch_size=10)
        processed_text = ''
        for token in text:
            token = token.text
            processed_toke = preprocess(paperid,token)
            if processed_toke == '':
                continue
            processed_text = processed_text +' '+token
        data = dataset.get(paperid)
        data['body'] = processed_text
        dataset.update({paperid:{data}})


def load_csv():
    global dataset
    counter = 0
    with open('./cord/'+date+'/metadata.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            doi = row['doi']
            title = row['title']
            abstract = row['abstract']
            publish_time = row['publish_time']
            paperid = row['pdf_json_files'][25:]
            if (not paperid == '' and not publish_time == '' and not abstract == '' and not title == '' and not doi == ''):
                if(not doi.startswith('http://dx.doi.org/')): doi = 'http://dx.doi.org/'+doi
                dataset.update({paperid:{'doi': doi, 'title': title, 'abstract': abstract, 'authors': '', 'publish_time': publish_time, 'body': ''}})
            counter = counter + 1
            if counter == MAX_FILE_NUMER:
                break

''' load_dataset function
    Loads the Dataset from file and downloads the file from server if file non existent
'''
def load_dataset():
    #dl.download()
    load_csv()
    parse_json()
    print("here is a stop")

''' connect_to_DB function
    Connect to the database
'''
def connect_to_DB():
    global db_host
    global db_user
    global db_password
    global db_database
    global populator_cursor
    global populator
    try:
        populator = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_database
        )
        populator_cursor=populator.cursor()
    except:
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
def add_object_to_DB(insert_sql, select_sql, val, populator) -> int:
    try:
        populator_cursor = populator.cursor()
        populator_cursor.execute(select_sql, val)
        id = populator_cursor.fetchone()
        if id is None:
            populator_cursor.execute(insert_sql, val)
            populator.commit()
            id = populator_cursor.lastrowid()
            return id
        else:
            return id
    except BaseException:
        exit(1)

def add_object_to_DB(instert_sql, select_sql, val) -> int:
    populator_cursor.execute(select_sql, val)
    try:  # Object already exists
        id = populator_cursor.fetchone()
    except:  # Object needs to be added
        populator_cursor.excute(instert_sql, val)
        populator.commit()
        id = populator_cursor.lastrowid()
    return id

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

        author_id = add_object_to_DB(insert_sqls['Author'], select_sqls['Author'], val_author)
        paper_id = add_object_to_DB(insert_sqls['Paper'], select_sqls['Paper'], val_paper)
        word_ids = []
        for word in val_word:
            word_ids.append(add_object_to_DB(insert_sqls['Word'], select_sqls['Word'], val_word))

''' count_unique function
    Counts the unique words in the document
'''
def count_unique(text) -> dict:
    tokens = text.split()
    token_dict = {}
    for t in tokens:
        c = token_dict.get(t,0)+1
        token_dict.update({t:c})
    return token_dict

if __name__ == "__main__":
    stem = False
    case_fold = False
    lemmatize = True
    stop_words = True
    load_dataset()
    connect_to_DB()
    populate()