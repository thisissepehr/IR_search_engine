import pickle
import sys
import math
import spacy
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import snowballstemmer
stemmer = snowballstemmer.stemmer("english")
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
case_fold = False

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
def bm25l(word_occ, word_count, doc_countm, contains_count, all_dwords_count, b = 0.75, delta = 0.5, k = 1.2):
    ctd = tf(word_occ, word_count) / (1 - b + b * word_count / avgdl(all_dwords_count, doc_count))
    return idf(doc_count, contains_count) * (k + 1) * (ctd + delta) / (k + ctd + delta)

# Function to calculate BM25Plus
def bm25_plus():
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
        for docno, u_c in unique_word_counters.items():
            if docno in word_counters: # Added condition
                sum_m = sum_m + avgtf(word_counters[docno], u_c)
        mavgtf_v = sum_m / doc_count
    return mavgtf_v

# Function to calculate BM25VA score
def bva(word_count, doc_count, all_dwords_count, unique_word_count):
    mavgtf_l = mavgtf(doc_count)
    return (pow(mavgtf_l, -2) * avgtf(word_count, unique_word_count) + (1 - pow(mavgtf_l, -1)) *
            word_count / avgdl(all_dwords_count, doc_count))

# Function to score query
def score_topic(topic_words, topic_word_count):
    topic_vector = {}
    for tk, tv in topic_words.items():
        if scoring_method == "tf-idf":
            topic_vector[tk] = (tf_idf(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1))
        elif scoring_method == "bm25":
            topic_vector[tk] = (bm25(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1,
                           word_counters["word_counter"]))
        elif scoring_method == "bm25va":
            b = bva(topic_word_count, word_counters["doc_counter"], word_counters["word_counter"], len(topic_words))
            topic_vector[tk] = (bm25(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1,
                           word_counters["word_counter"], b))
    return topic_vector

# Function to build vectors of query words
def build_vectors(topic_words, topic_word_count):
    topic_vector = score_topic(topic_words, topic_word_count)
    topic_vector = {}
    document_vectors = {}
    for tk, tv in topic_words.items():
        if scoring_method == "tf-idf":
            topic_vector[tk] = (tf_idf(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1))
        elif scoring_method == "bm25":
            topic_vector[tk] = (bm25(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1,
                           word_counters["word_counter"]))
        elif scoring_method == "bm25va":
            b = bva(topic_word_count, word_counters["doc_counter"], word_counters["word_counter"], len(topic_words))
            topic_vector[tk] = (bm25(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1,
                           word_counters["word_counter"], b))
        for dk, dv in iInd[tk].items():
            if scoring_method == "tf-idf":
                document_vectors[dk][tk] = tf_idf(dv, word_counters[dk], word_counters["doc_counter"], len(iInd[tk]) + 1)
            elif scoring_method == "bm25":
                document_vectors[dk][tk] = bm25(dv, word_counters[dk], word_counters["doc_counter"], len(iInd[tk]) + 1,
                               word_counters["word_counter"])
            elif scoring_method == "bm25va":
                b = bva(word_counters[dk], word_counters["doc_counter"], word_counters["word_counter"],
                        unique_word_counters[dk])
                document_vectors[dk][tk] = bm25(dv, word_counters[dk], word_counters["doc_counter"], len(iInd[tk]) + 1,
                               word_counters["word_counter"], b)
    return topic_vector, document_vectors

# Function to calculate the score
def score(topic_words, topic_word_count):
    scores_upper = {}
    vector_betrag_topic = 0
    vector_betrag_doc = {}
    for tk, tv in topic_words.items():
        if tk in iInd:
            if scoring_method == "tf-idf":
                t_score = tf_idf(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1)
            elif scoring_method == "bm25":
                t_score = bm25(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1,
                               word_counters["word_counter"])
            elif scoring_method == "bm25va":
                b = bva(topic_word_count, word_counters["doc_counter"], word_counters["word_counter"], len(topic_words))
                t_score = bm25(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1,
                               word_counters["word_counter"], b)
            vector_betrag_topic += t_score * t_score
            for dk, dv in iInd[tk].items():
                if dk in word_counters:
                    if scoring_method == "tf-idf":
                        d_score = tf_idf(dv, word_counters[dk], word_counters["doc_counter"], len(iInd[tk]) + 1)
                    elif scoring_method == "bm25":
                        d_score = bm25(dv, word_counters[dk], word_counters["doc_counter"], len(iInd[tk]) + 1,
                                       word_counters["word_counter"])
                    elif scoring_method == "bm25va":
                        b = bva(word_counters[dk], word_counters["doc_counter"], word_counters["word_counter"],
                                unique_word_counters[dk])
                        d_score = bm25(dv, word_counters[dk], word_counters["doc_counter"], len(iInd[tk]) + 1,
                                       word_counters["word_counter"], b)
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
print("Choose a scoring method. Options are: \"tf-idf\", \"bm25\" or \"bm25va\".")
scoring_method = input()
if scoring_method != "tf-idf" and scoring_method != "bm25" and scoring_method != "bm25va":
    print("Please either enter \"tf-idf\", \"bm25\" or \"bm25va\". Exiting..")
    sys.exit(0)

if os.path.exists('scores_{}.txt'.format(scoring_method)):
    os.remove('scores_{}.txt'.format(scoring_method))
    print('Output file scores_{}.txt already exists. Old file deleted.'.format(scoring_method))
    # sys.exit(0)

print("All data is being loaded. This can take a few minutes.")
iInd = pickle.load(open("inv_ind.p", "rb"))
word_counters = pickle.load(open("word_count.p", "rb"))
unique_word_counters = pickle.load(open("unique_words_count.p", "rb"))
nlp = spacy.load('en_core_web_sm')
print("Data loaded successfully, starting with scoring.")

topic_tokens = pre_process_query(query)
process_topic(topic_tokens, query, topicNo=None)

print("All topics processed. Output can be found in \"scores_{}.txt\".".format(scoring_method))


