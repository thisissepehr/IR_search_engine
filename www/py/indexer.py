import csv
import mysql.connector
import downloader as dl
import itertools
import os
import spacy
import json
import snowballstemmer

# The Date identifier of the dataset that should be used
date = '2022-03-31'

# global DB variables
db_host = "127.0.0.1"
db_port = "6033"
db_user = 'root' #'populator',
db_password = 'root' #'d9pifetoyesad2cekipoyolis',
db_database = "BASP"
insert_sqls = {'Author': 'INSERT INTO Author (FirstName, LastName) VALUES (%s, %s)',
               'Paper': 'INSERT INTO Paper (idPaper, title, doi,abstract,year,body,word_count,unique_word_count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
               'Word': 'INSERT INTO Word (word) VALUES (%s)',
               'paper_to_author': 'INSERT INTO paper_to_author (fk_paper_id, fk_author_id) VALUES (%s, %s)',
               'word_to_paper': 'INSERT INTO word_to_paper (fk_word_id, fk_paper_id,counter) VALUES (%s, %s,%s)'}
select_sqls = {'Author': 'SELECT * FROM Author WHERE FirstName = %s AND LastName = %s',
               'Paper': 'SELECT * FROM Paper WHERE idPaper = %s',
               'paper_to_author': 'SELECT * FROM paper_to_author WHERE fk_paper_id = %s AND fk_author_id = %s',
               'Word': 'SELECT * FROM Word WHERE word = %s',
               'word_to_paper': 'SELECT * FROM word_to_paper WHERE fk_word_id = %s AND fk_paper_id = %s'}

# global variables
dataset = {}
populator = None
populator_cursor = None
nlp = spacy.load('en_core_web_sm')
stemmer = snowballstemmer.stemmer("english")
MAX_FILE_NUMER = 10

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
            dataset.update({paperid:data})
            yield paperid, text_only

def preprocess(doc_id,token) -> str:
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
    texts = nlp.pipe(texts, batch_size=10)
    for paperid, texts in zip(paperids, texts):
        processed_text:str = ''
        for token in texts:
            processed_token:str = preprocess(paperid,token)
            if processed_token == '' or processed_token == None:
                continue
            processed_text = processed_text+' '+processed_token
        data = dataset.get(paperid)
        data['body'] = processed_text
        dataset.update({paperid:data})


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
            paperid = row['pdf_json_files'][25:].split()
            if (not len(paperid) == 0 and not publish_time == '' and not abstract == '' and not title == '' and not doi == ''):
                if(not doi.startswith('http://dx.doi.org/')): doi = 'http://dx.doi.org/'+doi
                dataset.update({paperid[0].replace(';',''):{'doi': doi, 'title': title, 'abstract': abstract, 'authors': '', 'publish_time': publish_time, 'body': ''}})
                counter = counter + 1
            if counter == MAX_FILE_NUMER:
                break

''' load_dataset function
    Loads the Dataset from file and downloads the file from server if file non existent
'''
def load_dataset():
    if not os.path.exists('./cord/'+date+'/metadata.csv'):
        dl.download()
    load_csv()
    parse_json()

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
    global db_port
    try:
        populator = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_database,
            port=db_port
        )
        populator_cursor=populator.cursor()
    except BaseException as ex:
        print(ex)
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
def add_object_to_DB(instert_sql, select_sql, select_val, val):
    populator_cursor = populator.cursor()
    populator_cursor.execute(select_sql, select_val)
    try: 
        id = populator_cursor.fetchone()
        if id == None:
            populator_cursor.execute(instert_sql, val)
            populator.commit()
            id = populator_cursor.lastrowid
    except BaseException as es: 
        print(es)
        exit(1)
    return id

''' index function
    All the indexing happens here
'''
def index(paper_id, author_ids, word_ids):
    if not type(paper_id)==str: paper_id = paper_id[0]
    for author_id  in author_ids:
        if not type(author_id)==int: author_id = author_id[0]
        # should checke first if exists
        add_object_to_DB(insert_sqls['paper_to_author'], select_sqls['paper_to_author'], (paper_id, author_id), (paper_id, author_id))
    populator.commit()
    for word_id,word_val in word_ids:
        if not type(word_id)==int: word_id = word_id[0]
        # should checke first if exists
        counter = dataset.get(paper_id)['body'].count(word_val)
        add_object_to_DB(insert_sqls['word_to_paper'], select_sqls['word_to_paper'], (word_id, paper_id), (word_id, paper_id,counter))
    populator.commit()

''' populate function
    Populates the Database
'''
def populate():
    for paperid,data in dataset.items():
        val_authors = [(author['first'],author['last']) for author in data['authors']]
        val_paper = (paperid,data['title'], data['doi'], data['abstract'], data['publish_time'], data['body'], len(data['body'].split()), len(count_unique(data['body'])))
        val_words = data['body'].split()
        paper_id = add_object_to_DB(insert_sqls['Paper'], select_sqls['Paper'], [paperid],val_paper)
        author_ids = []
        for val_author in val_authors:
            author_ids.append(add_object_to_DB(insert_sqls['Author'], select_sqls['Author'], val_author,val_author))
        word_ids = []
        for val_word in val_words:
            word_ids.append((add_object_to_DB(insert_sqls['Word'], select_sqls['Word'], [val_word],[val_word]),val_word))
        index(paperid, author_ids, word_ids)

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