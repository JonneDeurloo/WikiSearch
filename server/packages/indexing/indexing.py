#from ..common.article import Article
import pickle
import datetime
import os
import operator
import string
import unidecode
import math
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from dbmanager import dbmanager as DBM
#from ..dbmanager import dbmanager as DBM\



# GLOBAL VARIABLES
dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(dir_path, f'..\\common\\dataset')
file_titles = "article_titles.txt"
path_titles = file_path + f'\\{file_titles}'
file_articles = "articles_in_plain_text.txt"
path_articles = file_path + f'\\{file_articles}'
total_articles = 13385
n_terms = 398596


# Create a connection to the database
def create_connection():

    global db
    db = DBM.create_connection('indexing')


# Check if the wiki table exists in the database
def table_wiki_exists():

    cursor = db.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='wiki'")
    table = cursor.fetchone()
    return table != None

# Check if the docvec table exists in the database
def table_docvec_exists():

    cursor = db.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='docvec'")
    table = cursor.fetchone()
    return table != None


# Create the table wiki in the database
def create_table_wiki():

    cursor = db.cursor()
    cursor.execute(
        '''DROP TABLE IF EXISTS `wiki`''')
    cursor.execute(
        '''
		CREATE TABLE IF NOT EXISTS wiki(
			id 			INTEGER PRIMARY KEY,
			term 		TEXT unique,
			idf      	INTEGER)
	    ''')
    db.commit()


# Create the table wiki in the database
def create_table_docvec():

    cursor = db.cursor()
    cursor.execute(
        '''DROP TABLE IF EXISTS `docvec`''')
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS docvec(
            id 			INTEGER PRIMARY KEY,
            vec 	    TEXT)
        ''')
    db.commit()


# Create the indexing tables (wiki and docvec)
def create_indexing():

    # Check whether both tables exist
    if not table_wiki_exists() and not table_docvec_exists():

        # Create the wiki and docvec table
        create_table_wiki()
        create_table_docvec()

        # Get the dictionary with all the terms, idfs and document number with frequency
        # index_arts = calc_idfs(index_articles(path_articles, path_titles))

        # Uncomment to save indexes dictionary to a pickle file
        # pickle_out = open("indexes.pkl", "wb")
        # pickle.dump(index_arts, pickle_out)
        # pickle_out.close()

        # Uncomment to lead the pickle file of indexes dictionary
        pickle_in = open("indexes.pkl", "rb")
        index_arts = pickle.load(pickle_in)

        # Insert the terms and idfs to the database
        inv_index_list = indexdict_to_list(index_arts)
        cursor = db.cursor()
        cursor.executemany(
            '''INSERT INTO wiki(term, idf) VALUES(?, ?)''', inv_index_list)
        db.commit()
        inv_index_list = None



        # Insert the tfidf vector of all the terms for an article(doc) to the database
        doc_vec_list = tfidf_doc_vec(index_arts)

        # Uncomment to save dovecs dictionary to a pickle file
        # pickle_out = open("docvecs.pkl", "wb")
        # pickle.dump(doc_vec_list, pickle_out)
        # pickle_out.close()

        # Uncomment to lead the pickle file of indexes dictionary
        pickle_in = open("docvecs.pkl", "rb")
        doc_vec_list = pickle.load(pickle_in)

        cursor = db.cursor()
        cursor.executemany(
            '''INSERT INTO docvec(vec) VALUES(?)''', doc_vec_list)
        db.commit()


# Get the top 10 documents that are most similar to the query
def query_results(query):

    # Get tokens of the query
    query_tokens = tokenize_title(query)
    # Create a dictionary for the query tokens
    query_dict = {}
    # Create a vector for the tfidf values of a query
    query_vec = np.zeros(n_terms)
    # Create a list for the cosine similarity scores of the articles/documents
    sim_scores = []

    # For each token in the query
    for token in query_tokens:
        # Get the id of the token in the database and the idf
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, idf FROM wiki WHERE term = ?", (token, ))
        # Check if the token is in the database
        value = cursor.fetchone()
        if value != None:
            # If so add the id idf tuple to the query dictionary
            # value = cursor.fetchone()
            id_idf = (value[0], value[1])
            query_dict[token] = id_idf

    # For each term and id, idf tuple in the query dictionary
    for term, tup in query_dict.items():
        # Count the frequency/occurrences of the term in the query
        n = query_tokens.count(term)

        #calculate the weighted tf and tf.idf and append the value into the query vector
        tf = 1 + math.log10(n)
        tfidf = tf * tup[1]
        tfidf = round(tfidf, 4)
        term_id = tup[0] - 1
        query_vec[term_id] = (tfidf)

    cursor = db.cursor()
    cursor.execute('''SELECT id, vec FROM docvec''')
    tot_docvecs = cursor.fetchall()

    for (id_doc, docvecstring) in tot_docvecs:
        # docvec_dict = {}
        doc_vec = np.zeros(n_terms)

        id_tfidf_list = docvecstring.split(' ')
        for id_tfidf in id_tfidf_list:
            split = id_tfidf.split(':')
            term_id = int(split[0]) - 1
            tfidf = float(split[1])
            doc_vec[term_id] = tfidf

        #     docvec_dict[int(split[0])] = float(split[1])
        #
        # doc_vec = np.zeros(n_terms)
        #
        # for term, tup in query_dict.items():
        #     term_id = tup[0]
        #     if term_id in docvec_dict.keys():
        #         if term_id == 4200 and id_doc == 3938:
        #             print(docvec_dict[term_id], docvec_dict[tup[0]])
        #         doc_vec[term_id - 1] = docvec_dict[term_id]

        # Calculate the similarity score between the query and the document
        sim_score = cos_sim(query_vec, doc_vec)

        # If there is no score don't add it to the list of possible similar documents
        if (sim_score != 0.0):
            sim_scores.append((id_doc - 1, sim_score))

    # # For each article/document
    # for i in range(total_articles+1):
    #     print(i)
    #     if i == 0: continue
    #     # Get the documnent vector
    #     cursor = db.cursor()
    #     cursor.execute(
    #         "SELECT vec FROM docvec WHERE id = ?", (i,))
    #     value = cursor.fetchone()
    #
    #     # Split the string into a float vector of tf.idf values
    #     doc_vec = [float(x) for x in value[0].split(' ')]
    #
    #     # Resize the document vector to the size of the query
    #     doc_vec_q = []
    #
    #     # For each term and id, idf tuple in the query dictionary
    #     for term, tup in query_dict.items():
    #         # Get the id and append the idf value of that id in the document vector
    #         id = tup[0]
    #         doc_vec_q.append(doc_vec[id-1])
    #
    #     # Calculate the similarity score between the query and the document
    #     sim_score = cos_sim(query_vec, doc_vec_q)
    #
    #     # If there is no score don't add it to the list of possible similar documents
    #     if(sim_score != 0.0):
    #         sim_scores.append((i-1, sim_score))

    # Sort the list of similarity documents on cosine similarity score from high to low
    sim_scores.sort(key=operator.itemgetter(1), reverse=True)

    titles = article_title_list2(path_titles)
    for tup in sim_scores[:10]:
        print(titles[tup[0]])

    # return sim_scores[:10]



def documents_to_tfidf_vector(mydict):

    doc_vecs = []
    for i in range(total_articles):
        print('to tfidf article:', i)
        doc_vec = []
        for term, freq_docs in mydict.items():
            docs_counts = freq_docs[1]
            idf_term = freq_docs[0]
            tf_log = 0
            if i in docs_counts.keys():
                doc_count = docs_counts[i]
                tf_log = 1 + math.log10(doc_count)

            tfidf = tf_log * idf_term
            doc_vec.append(round(tfidf, 4))

        doc_vec_str = ' '.join(str(el) for el in doc_vec)

        doc_vecs.append([doc_vec_str])

    return doc_vecs


# Calculate the idfs of all the terms in the dictionary
def calc_idfs(mydict):

    i = 0
    # For each term in the dictionary
    for term, freq_docs in mydict.items():
        if i % 100 == 0:
            print('calcidf:', term)
        # Get the number of (distinct) occurrences of the term in all the documents (not total!)
        doc_freq = freq_docs[0]
        # Calculate the idf of the term
        idf_term = math.log10(float(total_articles) / float(doc_freq))
        freq_docs[0] = round(idf_term, 4)

        i += 1

    return mydict


# TODO: comments
def tfidf_doc_vec(mydict):

    doc_vecs = []
    for i in range(total_articles):
        print('docvec tfidf article:', i)

        doc_vec = []
        id_term = 1
        for term, freq_docs in mydict.items():
            docs_counts = freq_docs[1]
            idf_term = freq_docs[0]
            if i in docs_counts.keys():
                doc_count = docs_counts[i]
                tf_log = 1 + math.log10(doc_count)

                tfidf = tf_log * idf_term
                tfidf = round(tfidf, 4)
                id_idf_str = f"{id_term}:{tfidf}"
                doc_vec.append(id_idf_str)
            id_term += 1

        doc_vec_str = ' '.join(str(el) for el in doc_vec)
        doc_vecs.append([doc_vec_str])

    return doc_vecs



# TODO: comments
def indexdict_to_list(mydict):

    inv_index_list = []
    for k1, v1 in mydict.items():
        # doc_freq = v1[0]
        # idf_term = math.log10(float(total_articles) / float(doc_freq))
        # v1[0] = idf_term

        # cursor = db.cursor()
        # cursor.execute(
        #     '''INSERT INTO wiki(term, idf) VALUES(?, ?)''', (k1, idf_term))
        # db.commit()

        inv_index_list.append([k1, v1[0]])

    return inv_index_list
    #return mydict



# Reads a title file and gives all the titles without tokenization
def article_title_list2(file):

    titles = []
    # Read the file
    with open(file, 'r', encoding="utf8") as tf:
        # read each line
        for line in tf:
            # Remove the enters and add the title to the list
            newline = line.replace('\n', '')
            titles.append(newline)

    return titles


# Reads a title file and gives all the tokenized titles
def article_title_list(file):

    titles = []
    # Read the file
    with open(file, 'r', encoding="utf8") as tf:
        index = 0
        # Read each line
        for line in tf:
            # Tokenize the line and add the list of title-tokens to the titles-list
            tokens = tokenize_title(line)
            titles.append(tokens)

    return titles


# Tokenizes the title
def tokenize_title(string):

    # Remove enters
    string = string.replace('\n', '')
    # Lower the text
    string = string.lower()
    # Remove weird characters
    string = change_utf_to_ascii(string)
    # Replace - to a space, to indicate separate words
    string = string.replace('-', ' ')
    # Remove '
    string = string.replace('\'', '')
    # Tokenize the title with the nltk package
    token_string = word_tokenize(string)

    # Import stopwords from the nltk package
    stop_words = stopwords.words('english')
    # Check if a word is not a stopword and is also an acceptable word
    token_stop = [word for word in token_string
                  if word not in stop_words and check_viable_word(word)]
    # If the title only contains stopwords use the original tokenized title
    if len(token_stop) == 0:
        token_stop = token_string

    # Stem the word with the PorterStemmer function from the nltk package
    ps = PorterStemmer()
    token_stem = [ps.stem(word) for word in token_stop]

    return token_stem


# Makes a text file into a list of articles
def article_list(file):

    articles = []
    # Read the file
    with open(file, 'r', encoding="utf8") as tf:
        index = 0
        # Read each line
        for line in tf:
            # Delete enters and tabs
            line = line.replace('\n', ' ').replace('\t', ' ')
            # Split the text into the first word and the rest
            split = line.split(' ', 1)
            # Check if it is a new article
            if split[0] == '#Article:':
                # If so add it so a new element in the list and update the index
                articles.append(split[1])
                index += 1
            # Else if whitelines or (sub)titles don't check but continue
            elif line == ' ' or line[0] == '#':
                continue
            # Else add the line to the current element in the list
            else:
                articles[index-1] += line

    return articles


# Tokenizes the whole text article
def tokenize_article2(art_text):

    # Lower the text
    art_text = art_text.lower()
    # Remove weird characters
    art_text = change_utf_to_ascii(art_text)
    # Changes punctuation to spaces
    art_text = art_text.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
    # Tokenize and sort the article text with the nltk package
    sorted_tokens = sorted(word_tokenize(art_text))

    # Import stopwords and stem the word with PorterStemmer from the nltk package
    stop_words = stopwords.words('english')
    ps = PorterStemmer()
    # Check if a word is not a stopword and is also an acceptable word
    tokens_art_text = [ps.stem(word) for word in sorted_tokens
                       if word not in stop_words and check_viable_word(word)]

    return tokens_art_text


# Change the utf-8 text to ascii
def change_utf_to_ascii(text):

    # Create a result string
    res = ''
    # For each character in the text
    for i in range(len(text)):
        # Try the decode and encode the character to ascii
        try:
            c = text[i]
            s = unidecode.unidecode(c)
            s = s.encode(encoding='utf-8').decode('ascii')
            # Lower the character
            s = s.lower()
            # Check if it is a point or comma for numbers, and if so don't remove the character
            if (c == '.' or c == ',') and (text[i-1].isdigit() and text[i+1].isdigit()):
                s = s
            # Remove '
            elif s in '\'':
                s = ''
            # Replace punctuation for spaces
            elif s in string.punctuation:
                s = ' '
        # If there is an exception, change the character to a space
        except UnicodeDecodeError:
            s = ' '
        # Concatenate the character to the result string
        res += s

    return res


# Checks if a word is viable
def check_viable_word(word):
    # Check if the word is all digits or letters, TRUE (viable)
    if all(c in string.digits or c in string.ascii_lowercase for c in word):
        return True
    # Check if the word is all punctuation, FALSE (NOT viable)
    elif all(c in string.punctuation for c in word):
        return False
    # Check if the word is not all punctuation, TRUE (viable)
    elif all(c in string.digits or c in string.ascii_lowercase or c in string.punctuation for c in word):
        return True
    # Just a check if there is any other case, and if so also FALSE (NOT viable)
    else:
        print(word)
        return False


# Invert index the text articles
def index_articles(article_text, article_title):

    # Create a dictionary
    index_dict = {}
    # Get the articles as a list of articles
    articles = article_list(article_text)
    # Get the tokens for a title as a list
    titles = article_title_list(article_title)
    for counter, title in enumerate(titles):
        if counter % 100 == 0:
            print('Doing new title', counter, '...')

        # Get the set of tokens
        tokens_set = set(title)
        # Go through each unique token
        for token in tokens_set:
            # Check if the token is not in the term index dictionary
            if token not in index_dict:
                # If not add the token, initiate the unique counter for the term and a new dictionary
                index_dict[token] = [1, {}]
            # Else add 1 to the unique counter
            else:
                index_dict[token][0] += 1

        # Go through all the tokens again (Not unique ones)
        for token in title:
            # If there is already a counter for the article increase the counter
            if counter in index_dict[token][1]:
                index_dict[token][1][counter] += 1
            # Else create a counter for the article
            else:
                index_dict[token][1][counter] = 1

    # Go through each article
    for counter, art in enumerate(articles):
        if counter % 100 == 0:
            print('Doing new article', counter, '...')
        # Tokenize the article
        tokens = tokenize_article2(art)
        # Get the set of tokens
        tokens_set = set(tokens)
        # Go through each unique token
        for token in tokens_set:
            # Check if the token is not in the term index dictionary
            if token not in index_dict:
                # If not add the token, initiate the unique counter for the term and a new dictionary
                index_dict[token] = [1, {}]
            # Else add 1 to the unique counter
            else:
                index_dict[token][0] += 1

        # Go through all the tokens again (Not unique ones)
        for token in tokens:
            # If there is already a counter for the article increase the counter
            if counter in index_dict[token][1]:
                index_dict[token][1][counter] += 1
            # Else create a counter for the article
            else:
                index_dict[token][1][counter] = 1

    return index_dict

# Calculate the length of a vector
def length_vec(x):
    # Calculate the dotproduct of the vector with itself and take the square root of it
    return math.sqrt(np.dot(x, x))

# Calculate the cosine similarity between two vectors
def cos_sim(a, b):
    # Calculate the dot product between the two vectors
    numerator = np.dot(a, b)
    # Calculate the lengths of both vectors and multiply them
    denomerator = length_vec(a) * length_vec(b)

    # Check if denomerator is 0, if so return 0
    if denomerator == 0.0:
        return 0.0
    # Else calculate and return the cosine sim
    else:
        return numerator / denomerator


now = datetime.datetime.now()
print('start:', now)

create_connection()
create_indexing()
print("\n---------------\n")

query = "Cosine Similarity"
query_results(query)

end = datetime.datetime.now()
print('\nend:', datetime.datetime.now())
print('diff:', end - now)