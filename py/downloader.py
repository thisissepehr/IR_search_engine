import csv
import os
import json
from collections import defaultdict
import requests
import tarfile

cord_uid_to_text = defaultdict(list)


date = '2020-03-13'

def donwload():
    url = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases/cord-19_"+date+".tar.gz"
    r = requests.get(url)
    with open("cord.tar.gz", 'wb') as f:
        f.write(r.content) 
    file = tarfile.open('cord.tar.gz')
    file.extractall('./cord')
    file.close()


dataset = []
with open('./cord/'+date+'/all_sources_metadata_'+date+'.csv') as f_in:
    reader = csv.DictReader(f_in)
    for row in reader:
        doi = row['doi']
        title = row['title']
        abstract = row['abstract']
        authors = row['authors']
        has_full_text = row['has_full_text']
        publish_time = row['publish_time']
        if (has_full_text and not publish_time == '' and not abstract == '' and not authors == '' and not title == '' and not doi == ''):
            if(not  doi.startswith('http://dx.doi.org/')): doi = 'http://dx.doi.org/'+doi
            dataset.append({'doi':doi,'title':title,'abstract':abstract,'authors':authors, 'publish_time':publish_time})
    print(len(dataset))