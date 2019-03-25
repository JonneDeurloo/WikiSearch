#from ..common.article import Article

import sys
import os
import csv
import json
import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from ..dbmanager import dbmanager as DBM
from ..common.wiki_parser import wiki_parser as wp



def create_connection():
    """ Create a database connection to an SQLite database """

    global db

    db = DBM.create_connection('indexing')


def create_table_wiki():
    """ Create wiki table (if not exists) """

    cursor = db.cursor()
    cursor.execute(
        '''DROP TABLE IF EXISTS `wiki`''')
    cursor.execute(
        '''
		CREATE TABLE IF NOT EXISTS wiki(
			id 			INTEGER PRIMARY KEY,
			term 		TEXT unique,
			counter 	INTEGER,
            indexes     TEXT)
	    ''')
    db.commit()


def table_wiki_exists():
    cursor = db.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='wiki'")
    table = cursor.fetchone()
    return table != None


def get_all_from_wiki():
    """ Get all values from the wiki table """

    cursor = db.cursor()
    cursor.execute('''SELECT term, counter, indexes FROM wiki''')
    return cursor.fetchall()


def create_wiki(file):
    """ Build the Wiki table """

    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, f'..\common\dataset\{file}\{file}')

    wp.xml_to_csv(file_path + '.xml')

    with open(file_path + '.csv', encoding="utf8") as csvfile:
        wikireader = csv.DictReader(csvfile, delimiter='?', quotechar='|')
        wiki_insert = []
        for row in wikireader:
            if (len(tuple(row.values())) > 2):
                print(tuple(row.values()))  # Should not happen

            wiki_insert.append(tuple(row.values()))

        cursor = db.cursor()
        cursor.executemany(
            '''INSERT INTO wiki(title, links) VALUES(?,?)''', wiki_insert)
        db.commit()


def create_indexing():
   """ Build the indexing table """

   if not table_wiki_exists():
       create_table_wiki()
       create_wiki('enwiki-20190301')

   __create_graph()
   pr = nx.pagerank(G, alpha=0.9)

   cursor = db.cursor()
   cursor.executemany(
       '''UPDATE wiki SET pagerank = ? WHERE title = ?''', [t[::-1] for t in list(pr.items())])
   db.commit()




def indexdict_to_string(mydict):

    for k1, v1 in mydict.items():
        index_string = ''
        for k2, v2 in mydict[k1][1].items():
            temp = "{}:{} ".format(k2, v2)
            index_string += temp
        index_string = index_string[:-1]
        mydict[k1][1] = index_string

    return mydict


def article_title_list(file):

    titles = []
    # read the file
    with open(file, 'r', encoding="utf8") as tf:
        index = 0
        # read each line
        for line in tf:
            newline = line.replace('\n', '')
            newline = newline.lower()
            newline = newline.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
            newline_split = newline.split(' ')

            ps = PorterStemmer()
            newline_stemmed = [ps.stem(word) for word in newline_split if word != '']

            titles.append(newline_stemmed)

    # return all the articles
    return titles



# makes a text file into a list of articles
def article_list(file):

    articles = []
    # read the file
    with open(file, 'r', encoding="utf8") as tf:
        index = 0
        # read each line
        for line in tf:
            # delete enters and tabs
            line = line.replace('\n', ' ').replace('\t', ' ')
            # split the text into the first word and the rest
            split = line.split(' ', 1)
            # check if it is a new article
            if split[0] == '#Article:':
                # if so add it so a new element in the list and update the index
                articles.append(split[1])
                index += 1
            # else if whitelines or (sub)titles don't check but continue
            elif line == ' ' or line[0] == '#':
                continue
            # else add the line to the current element in the list
            else:
                articles[index-1] += line

    # return all the articles
    return articles


# tokenizes the whole text article
def tokenize_article(art_text):

    # transform the text by lowering, removing punctuation and stopwords, and stemming the text
    art_text = art_text.lower()
    art_text = art_text.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
    token_art_text = art_text.split(' ')

    stop_words = stopwords.words('english')
    ps = PorterStemmer()
    token_art_text = [ps.stem(word) for word in token_art_text if word not in stop_words and word != '']

    #return the tokenized article
    return token_art_text


# invert index the text articles
def index_articles(article_text, article_title):

    index_dict = {}
    titles = article_title_list(article_title)
    articles = article_list(article_text)
    #for counter, title in enumerate(titles):
    #    print('Doing new title', counter, '...')
    #    for token in title:
    #        if token not in index_dict:
    #            index_dict[token] = [1, {}]
    #            index_dict[token][1][counter] = 1
    #        else:
    #            index_dict[token][0] += 1
    #            if counter in index_dict[token][1]:
    #                index_dict[token][1][counter] += 1
    #            else:
    #                index_dict[token][1][counter] = 1
    for counter, art in enumerate(articles):
        print('Doing new article', counter, '...')
        tokens = tokenize_article(art)
        for token in tokens:
            if token not in index_dict:
                index_dict[token] = [1, {}]
                index_dict[token][1][counter] = 1
            else:
                index_dict[token][0] += 1
                if counter in index_dict[token][1]:
                    index_dict[token][1][counter] += 1
                else:
                    index_dict[token][1][counter] = 1

    return index_dict

file_articles = "articles_in_plain_text_test1.txt"
file_titles = "article_titles.txt"
inv_index = index_articles(file_articles, file_titles)
test = indexdict_to_string(inv_index)

print(test)
#print(inv_index)

exDict = {'exDict': inv_index}

with open('test.txt', 'w') as file:
     file.write(json.dumps(exDict))




#file = "articles_in_plain_text_test.txt"
#art = article_list(file)
#print(tokenize_article(art[0]))
#print("================================================================================================================================")
#print(art[1])
#print("================================================================================================================================")
#print(art[2])





#from ..common.article.article import Article

#def get_similar(query):
#    a1 = Article(1, query, "This is the first result")
#    a2 = Article(2, "Planet", "This is the second result")
#    a3 = Article(3, "Mars", "This is the thirth result")
#    a4 = Article(4, "Jupiter", "This is the fourth result")
#    return [a1, a2, a3, a4]
