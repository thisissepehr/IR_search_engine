import csv
import mysql.connector
import downloader as dl

# The Date itenifier of the datset that should be used
date = '2020-03-13'

#global DB variables
db_host="localhost",
db_user="populator",
db_password="d9pifetoyesad2cekipoyolis",
db_database="BASP"
select_sqls = {'Author': '', 'Paper': '', 'Word': ''}# TODO: add the SQL SELECT statements
instert_sqls = {'Author': '', 'Paper': '', 'paper_to_author': '','Word': '', 'word_to_paper': ''}  # TODO: add the SQL INSERT statements

#global variables
dataset = []
populator = None
populator_cursor = None

''' load_dataset function
    Loads the Dataset from file and downloads the file from server if file non existent
'''
def load_dataset():
    global dataset
    if True: #TODO replace with file './cord/'+date+'/all_sources_metadata_'+date+'.csv' exists
        dl.download()
    with open('./cord/'+date+'/all_sources_metadata_'+date+'.csv') as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            doi = row['doi']
            title = row['title']
            abstract = row['abstract']
            authors = row['authors']
            has_full_text = row['has_full_text']
            publish_time = row['publish_time']
            body = ''  # TODO get full text
            if (has_full_text and not publish_time == '' and not abstract == '' and not authors == '' and not title == '' and not doi == ''):
                if(not doi.startswith('http://dx.doi.org/')):
                    doi = 'http://dx.doi.org/'+doi
                dataset.append({'doi': doi, 'title': title, 'abstract': abstract,
                               'authors': authors, 'publish_time': publish_time, 'body': body})


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
            database=db_database,
            populator_cursor=populator.cursor()
        )
    except:
        exit(1)


''' add_object_to_DB function
    Adds a Object to the DB
    
    @param instert_sql
        the SQL insert statement needed to add this object
    @param select_sql
        the SQL select statement needed check if it already exists and retive in case it dose
    @param val
        the object attributes
    
    @return
        the object id
'''
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
def index(paper_id,author_id,word_ids):
    populator_cursor.excute(instert_sqls['paper_to_author'], (paper_id, author_id))
    populator.commit()
    for word_id in word_ids:
        populator_cursor.excute(instert_sqls['word_to_paper'], (word_id, paper_id))
        populator.commit()

''' populate function
    Populates the Database
'''
def populate():
    for entry in dataset:
        val_author = entry['authors']# TODO this string to be split to match the SQL statements
        val_paper = (entry['title'], entry['doi'], entry['abstract'], entry['publish_time'], entry['body'], len(entry['body'].split()))
        val_word = entry['body'].split()

        author_id = add_object_to_DB(instert_sqls['Author'], select_sqls['Author'], val_author)
        paper_id = add_object_to_DB(instert_sqls['Paper'], select_sqls['Paper'], val_paper)
        word_ids = []
        for word in val_word:
            word_ids.append(add_object_to_DB(instert_sqls['Word'], select_sqls['Word'], val_word))

        index(paper_id,author_id,word_ids)

if __name__=="__main__":
    load_dataset()
    connect_to_DB()
    populate()