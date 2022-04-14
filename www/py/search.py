import math
import spacy
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import snowballstemmer
import mysql.connector
stemmer = snowballstemmer.stemmer("english")
nlp = spacy.load('en_core_web_sm')
tokenizer = RegexpTokenizer(r'[a-zA-Z]+')
import sys, getopt
import json


# Input Query Preprocessor
lemmatize = True
stem = False
stop_words = True
case_fold = True

# global DB variables
db_host = "127.0.0.1"
db_port = "6033"
db_user = 'root' #'populator',
db_password = 'root' #'d9pifetoyesad2cekipoyolis',
db_database = "BASP"
select_sqls = {'word_counter': 'SELECT COUNT(*) FROM Word',
               'doc_counter': 'SELECT COUNT(*) FROM Paper',
               'word_in_doc_counter': 'SELECT COUNT(*) FROM word_to_paper WHERE fk_word_id in (SELECT idWord from Word WHERE word = %s)',
               'unique_word_counter': 'SELECT unique_word_count FROM Paper WHERE idPaper = %s',
               'word_avail': 'SELECT * FROM Word WHERE word = %s',
               'documents': 'SELECT fk_paper_id, counter FROM word_to_paper WHERE fk_word_id in (SELECT idWord from Word WHERE word = %s)',
               'total_words_in_doc': 'SELECT word_count from Paper WHERE idPaper = %s',
               'get_doc_unique_count': 'SELECT idPaper, word_count, unique_word_count FROM Paper'}

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

# Function to calculate term frequency
def tf(word_occ, word_count):
    return word_occ / word_count

# Function to calculate inverse document frequency
def idf(doc_count, contains_count):
    return math.log(doc_count / contains_count)

# Function to get average document length
def avgdl(all_dwords_count, doc_count):
    return all_dwords_count / doc_count

# Function to calculate TF-IDF score
def tf_idf(word_occ, word_count, doc_count, contains_count):
    return tf(word_occ, word_count) * idf(doc_count, contains_count)

# Function to calculate BM25 score
def bm25(word_occ, word_count, doc_count, contains_count, all_dwords_count, b=0.75, k=1.2):
    return (idf(doc_count, contains_count) * (tf(word_occ, word_count) * (k + 1)) /
            (tf(word_occ, word_count) + k * (1 - b + b * word_count / avgdl(all_dwords_count, doc_count))))

# Function to calculate BM25L
def bm25l(word_occ, word_count, doc_count, contains_count, all_dwords_count, b=0.75, delta=0.5, k=1.2):
    ctd = tf(word_occ, word_count) / (1 - b + b * word_count / avgdl(all_dwords_count, doc_count))
    return idf(doc_count, contains_count) * (k + 1) * (ctd + delta) / (k + ctd + delta)

# Function to calculate BM25Plus
def bm25_plus(word_occ, word_count, doc_count, contains_count, all_dwords_count, b=0.75, delta=0.5, k=1.2):
    return idf(doc_count, contains_count) * (delta + (tf(word_occ, word_count) * (k + 1)) / 
            (k * (1 - b + b * word_count / avgdl(all_dwords_count, doc_count)) + tf(word_occ, word_count)))

mavgtf_v = None

# Function to calculate average term frequency
def avgtf(word_count, unique_word_count):
    return word_count / unique_word_count

def mavgtf(doc_count):
    global mavgtf_v
    if mavgtf_v is None:
        sum_m = 0
        # Get all papers with unique word count from database
        unique_word_counters = get_val_from_DB(select_sqls['get_doc_unique_count'], None, False, False)
        for docno, word_count, u_c in unique_word_counters:
            sum_m = sum_m + avgtf(int(word_count), int(u_c))
        mavgtf_v = sum_m / doc_count
    return mavgtf_v

# Function to calculate BM25VA score
def bva(word_count, doc_count, all_dwords_count, unique_word_count):
    mavgtf_l = mavgtf(doc_count)
    return (pow(mavgtf_l, -2) * avgtf(int(word_count), unique_word_count) + (1 - pow(mavgtf_l, -1)) *
            int(word_count) / avgdl(all_dwords_count, doc_count))

def get_val_from_DB(select_sql, select_val, val, count):
    try:
        if val:
            populator_cursor.execute(select_sql, select_val)
            if count:
                id = populator_cursor.fetchone()
            else:
                id = populator_cursor.fetchall()
        else:
            populator_cursor.execute(select_sql)
            if count:
                id = populator_cursor.fetchone()
            else:
                id = populator_cursor.fetchall()
        if id is None:
            return -1
    except BaseException as es: 
        print(es)
        exit(1)
    return id

# Function to calculate the score
def score(topic_words, topic_word_count, scoring_method):
    scores_upper = {}
    vector_betrag_topic = 0
    vector_betrag_doc = {}
    for tk, tv in topic_words.items():
        # Find if that word is available in our database
        id = get_val_from_DB(select_sqls['word_avail'], (tk, ), True, True)
        if id != -1:
            # Get total number of words in whole dataset
            word_counters = get_val_from_DB(select_sqls['word_counter'], None, False, True)
            # Get total number of documents in dataset
            doc_counter = get_val_from_DB(select_sqls['doc_counter'], None, False, True)
            # Get total number of documents where we find word tk
            iInd = get_val_from_DB(select_sqls['word_in_doc_counter'], (tk, ), True, True)
            if scoring_method == "tf-idf":
                t_score = tf_idf(tv, topic_word_count, int(doc_counter[0]), int(iInd[0]) + 1)
            elif scoring_method == "bm25l":
                t_score = bm25l(tv, topic_word_count, int(doc_counter[0]), int(iInd[0]) + 1, int(word_counters[0]))
            elif scoring_method == "bm25_plus":
                t_score = bm25_plus(tv, topic_word_count, int(doc_counter[0]), int(iInd[0]) + 1, int(word_counters[0]))
            elif scoring_method == "bm25":
                t_score = bm25(tv, topic_word_count, int(doc_counter[0]), int(iInd[0]) + 1, int(word_counters[0]))
            elif scoring_method == "bm25va":
                b = bva(topic_word_count, int(doc_counter[0]), int(word_counters[0]), len(topic_words))
                t_score = bm25(tv, topic_word_count, int(doc_counter[0]), int(iInd[0]) + 1, int(word_counters[0]), b)
            elif scoring_method == 'bm25l':
                t_score = bm25l(tv, topic_word_count, int(doc_counter[0]), int(iInd[0]) + 1, int(word_counters[0]))
            elif scoring_method == "bm25_plus":
                t_score = bm25_plus(tv, topic_word_count, int(doc_counter[0]), int(iInd[0]) + 1, int(word_counters[0]))
            vector_betrag_topic += t_score * t_score

            # Get all documents & count of that word where we find work tk from word_to_paper Table
            documents = get_val_from_DB(select_sqls['documents'], (tk, ), True, False)
            for dk, dv in documents:
                # Get unique word counts in a document dk
                unique_word_counters = get_val_from_DB(select_sqls['unique_word_counter'], (dk, ), True, False)
                # get total word counts in document dk
                words_in_doc = get_val_from_DB(select_sqls['total_words_in_doc'], (dk, ), True, False)
                if scoring_method == "tf-idf":
                    d_score = tf_idf(dv, int(words_in_doc[0][0]), int(doc_counter[0]), int(iInd[0]) + 1)
                elif scoring_method == "bm25":
                    d_score = bm25(dv, int(words_in_doc[0][0]), int(doc_counter[0]), int(iInd[0]) + 1, int(word_counters[0]))
                elif scoring_method == "bm25l":
                    d_score = bm25l(dv, int(words_in_doc[0][0]), int(doc_counter[0]), int(iInd[0]) + 1, int(word_counters[0]))
                elif scoring_method == "bm25_plus":
                    d_score = bm25_plus(dv, int(words_in_doc[0][0]), int(doc_counter[0]), int(iInd[0]) + 1, int(word_counters[0]))
                elif scoring_method == "bm25va":
                    b = bva(int(words_in_doc[0][0]), int(doc_counter[0]), int(word_counters[0]), int(unique_word_counters[0][0]))
                    d_score = bm25(dv, int(words_in_doc[0][0]), int(doc_counter[0]), int(iInd[0]) + 1, int(word_counters[0]), b)
                elif scoring_method == 'bm25l':
                    d_score = bm25l(dv, int(words_in_doc[0][0]), int(doc_counter[0]), int(iInd[0]) + 1, int(word_counters[0]))
                elif scoring_method == "bm25_plus":
                    d_score = bm25_plus(dv, int(words_in_doc[0][0]), int(doc_counter[0]), int(iInd[0]) + 1, int(word_counters[0]))
                
                if scores_upper.get(dk) is None:
                    scores_upper[dk] = t_score * d_score
                else:
                    scores_upper[dk] = scores_upper[dk] + t_score * d_score
                if vector_betrag_doc.get(dk) is None:
                    vector_betrag_doc[dk] = d_score * d_score
                else:
                    vector_betrag_doc[dk] = vector_betrag_doc[dk] + d_score * d_score

    # cosine similarity
    vector_betrag_topic = math.sqrt(vector_betrag_topic)
    scores = {}
    for doc, upper in scores_upper.items():
        scores[doc] = upper / (vector_betrag_topic * math.sqrt(vector_betrag_doc[doc]))
    return scores

# Function to output the results
def output_topic(scores):
    MAX_OUTPUT = 100
    output = []
    for paper_id in [k for k in sorted(scores, key=scores.get, reverse=True)]:
        populator_cursor.execute('SELECT title,doi,year FROM Paper WHERE idPaper = %s', [paper_id])
        paper = populator_cursor.fetchone()
        populator_cursor.execute('SELECT FirstName,LastName FROM paper_to_author LEFT JOIN Author ON idAuthor=fk_author_id WHERE fk_paper_id = %s', [paper_id])
        authors = populator_cursor.fetchall()
        output.append({'title':paper[0], 'author':[author[0]+' '+author[1] for author in authors],'url':paper[1], 'year': paper[2].year})
        MAX_OUTPUT -= 1
        if MAX_OUTPUT == 0: break
    jsonString = json.dumps(output, indent=4)
    print(jsonString)
    

# Main function to process the query
def process_topic(docs, query, scoring_method):
    topic_words = {}
    word_count = 0

    for token in docs:
        # for token in doc:
        # if token.is_alpha and not token.is_stop and len(token.orth_) > 1:
        word_count = word_count + 1
        # strtok = token.lemma_.strip()
        if token not in topic_words.keys():
            topic_words[token] = 1
        else:
            topic_words[token] = topic_words[token] + 1

    scores = score(topic_words, word_count, scoring_method)
    output_topic(scores)

# Function to preprocess the query
def pre_process_query(query):
    tokens = []
    query = query.lower()
    docs = nlp(query)
    for token in docs:
        # filter out stopwords
        if not stop_words or (token.is_alpha and not token.is_stop and len(token.orth_) > 1):
            strtok = token.lemma_.strip() if lemmatize else token.orth_.strip()
            if case_fold:
                strtok = strtok.casefold()
            if stem:
                strtok = stemmer.stemWord(strtok)
            tokens.append(strtok)
    return tokens

def main_args(argv):
    query = 'ahead'
    scoring_method = 'bm25'
    try:
        opts, args = getopt.getopt(argv,"m:q:",[])
    except getopt.GetoptError:
        #exit(1)
        i=1
    for opt, arg in opts:
        if opt == '-m':
            scoring_method = str(arg)
        elif opt in ("-q"):
            query = str(arg)
    if query == '' and scoring_method == '': exit(1)

    connect_to_DB()
    topic_tokens = pre_process_query(query)
    process_topic(topic_tokens, query, scoring_method)    

if __name__ == "__main__":
   main_args(sys.argv[1:])