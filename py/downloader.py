import requests
import tarfile

# The Date itenifier of the datset that should be used
date = '2020-03-13'

''' load_dataset function
    Downloads the file from the server and saves it in the cord folder
'''
def download():
    url = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases/cord-19_"+date+".tar.gz"
    r = requests.get(url)
    with open("cord.tar.gz", 'wb') as f:
        f.write(r.content)
    file = tarfile.open('cord.tar.gz')
    file.extractall('./cord')
    file.close()