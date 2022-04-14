import pickle
import sys
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
import os

# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context
#
# nltk.download('omw-1.4')

# Input Query Preprocessor
lemmatize = True
stem = False
stop_words = True
case_fold = True

# global DB variables
db_host = "localhost"
db_port = "3306"
db_user = 'root' #'populator',
db_password = 'SED_Group10' #'d9pifetoyesad2cekipoyolis',
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

def get_val_from_DB(select_sql, select_val, val, count) -> int:
    populator_cursor = populator.cursor()
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
def score(topic_words, topic_word_count):
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
                pass
                ## TODO : 
            elif scoring_method == "bm25_plus":
                pass
                ## TODO :
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
                    pass
                    ## TODO : 
                elif scoring_method == "bm25_plus":
                    pass
                    ## TODO :
                
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
def output_topic(scores, query, topicNo):
    output_file = open('scores_{}.txt'.format(scoring_method), 'a')
    rank_counter = 1
    output_file.write("Input Query: {}\n".format(query))
    output_file.write("{} {} {} {} \n".format("topicNo", "score[0]", "rank_counter", "score[1]"))
    for score in [(k, scores[k]) for k in sorted(scores, key=scores.get, reverse=True)]:
        output_file.write("{} {} {} {} \n".format(topicNo, score[0], rank_counter, score[1]))
        rank_counter += 1
        if rank_counter == 1001:
            break
    output_file.close()

# Main function to process the query
def process_topic(docs, query, topicNo):
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

    scores = score(topic_words, word_count)
    output_topic(scores, query, topicNo)

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

# Take query input from user
print("Input your query: ")
query: str = input()

# Take scoring method input from user
print("Choose a scoring method. Options are: \"tf-idf\", \"bm25\", \"bm25l\", \"bm25_plus\" or \"bm25va\".")
scoring_method = input()
if scoring_method != "tf-idf" and scoring_method != "bm25" and scoring_method != "bm25va":
    print("Please either enter \"tf-idf\", \"bm25\" or \"bm25va\" \"bm25l\", \"bm25_plus\". Exiting..")
    sys.exit(0)

if os.path.exists('scores_{}.txt'.format(scoring_method)):
    os.remove('scores_{}.txt'.format(scoring_method))
    print('Output file scores_{}.txt already exists. Old file deleted.'.format(scoring_method))
    # sys.exit(0)

# print("All data is being loaded. This can take a few minutes.")
# iInd = pickle.load(open("inv_ind.p", "rb"))
# word_counters = pickle.load(open("word_count.p", "rb"))
# unique_word_counters = pickle.load(open("unique_words_count.p", "rb"))
# nlp = spacy.load('en_core_web_sm')
# print("Data loaded successfully, starting with scoring.")

connect_to_DB()
topic_tokens = pre_process_query(query)
process_topic(topic_tokens, query, topicNo=None)

print("All topics processed. Output can be found in \"scores_{}.txt\".".format(scoring_method))


