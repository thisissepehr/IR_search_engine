import csv
import requests
import tarfile
import mysql.connector

date = '2020-03-13'
download = False

def donwload():
    url = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases/cord-19_"+date+".tar.gz"
    r = requests.get(url)
    with open("cord.tar.gz", 'wb') as f:
        f.write(r.content) 
    file = tarfile.open('cord.tar.gz')
    file.extractall('./cord')
    file.close()

dataset = []
if download: download()
with open('./cord/'+date+'/all_sources_metadata_'+date+'.csv') as f_in:
    reader = csv.DictReader(f_in)
    for row in reader:
        doi = row['doi']
        title = row['title']
        abstract = row['abstract']
        authors = row['authors']
        has_full_text = row['has_full_text']
        publish_time = row['publish_time']
        body = '' #TODO get full text
        if (has_full_text and not publish_time == '' and not abstract == '' and not authors == '' and not title == '' and not doi == ''):
            if(not  doi.startswith('http://dx.doi.org/')): doi = 'http://dx.doi.org/'+doi
            dataset.append({'doi':doi,'title':title,'abstract':abstract,'authors':authors, 'publish_time':publish_time, 'body':body})
    print(len(dataset))

try:
    populator = mysql.connector.connect(
    host="localhost",
    user="populator",
    password="d9pifetoyesad2cekipoyolis",
    database="BASP"
    )


    populator_cursor = populator.cursor()    

    select_sqls = {'Author':'','Paper':'','Word':''} #TODO: add the SQL SELECT statements
    instert_sqls = {'Author':'','Paper':'','paper_to_author':'','Word':'','word_to_paper':''} #TODO: add the SQL INSERT statements
    
    for entry in dataset:
        
        val_author = entry['authors'] #TODO this string to be split to match the SQL statements
        val_paper = (entry['title'],entry['doi'],entry['abstract'],entry['publish_time'],entry['body'],len(entry['body'].split()))
        val_word = entry['body'].split()
        
        populator_cursor.execute(select_sqls['Author'],val_author)
        try: #Author already exists
            author_id = populator_cursor.fetchone()
        except: #Author needs to be added
            populator_cursor.excute(instert_sqls['Author'],val_author)
            populator.commit()
            author_id = populator_cursor.lastrowid()

        #add paper
        populator_cursor.excute(instert_sqls['Paper'],val_paper)
        populator.commit()
        paper_id = populator_cursor.lastrowid()

        word_ids = []
        for word in val_word:
            populator_cursor.execute(select_sqls['Word'],val_word)
            try: #Word already exists
                word_ids.append(populator_cursor.fetchone())
            except: #Word needs to be added
                populator_cursor.excute(instert_sqls['Word'],val_word)
                populator.commit()
                word_ids.append(populator_cursor.lastrowid())

        populator_cursor.excute(instert_sqls['paper_to_author'],(paper_id,author_id))
        populator.commit()
        for word_id in word_ids:
            populator_cursor.excute(instert_sqls['word_to_paper'],(word_id,paper_id))
            populator.commit()

except:
    print('DB connection error')
