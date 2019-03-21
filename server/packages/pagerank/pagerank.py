import matplotlib.pyplot as plt
import networkx as nx
import operator
import csv
import os
import sqlite3
from sqlite3 import Error

from ..common.article.article import Article
from ..dbmanager import dbmanager as DBM
from ..common.wiki_parser import wiki_parser as wp


def create_connection():
    """ Create a database connection to an SQLite database """

    global db

    db = DBM.create_connection('pr')


def create_table_wiki():
    """ Create wiki table (if not exists) """

    cursor = db.cursor()
    cursor.execute(
        '''DROP TABLE IF EXISTS `wiki`''')
    cursor.execute(
        '''
		CREATE TABLE IF NOT EXISTS wiki(
			id 			INTEGER PRIMARY KEY,
			title 		TEXT unique,
			links 		TEXT)
	    ''')
    db.commit()


def create_table_pagerank():
    """ Create PageRank table (if not exists) """

    cursor = db.cursor()
    cursor.execute(
        '''DROP TABLE IF EXISTS `pr`''')
    cursor.execute(
        '''
		CREATE TABLE IF NOT EXISTS pr(
			id 			INTEGER PRIMARY KEY,
			title 		TEXT unique,
			pagerank	FLOAT)
	    ''')
    db.commit()


def get_all_from_wiki():
    """ Get all values from the wiki table """

    cursor = db.cursor()
    cursor.execute('''SELECT title, links FROM wiki''')
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


def create_pagerank():
    """ Build the PageRank table """

    __create_graph()
    pr = nx.pagerank(G, alpha=0.9)

    cursor = db.cursor()
    cursor.executemany(
        '''INSERT INTO pr(title, pagerank) VALUES(?,?)''', list(pr.items()))
    db.commit()


def __create_graph():
    """ Create a directed graph based on the Wikipedia article links"""

    global G
    G = nx.DiGraph()

    all_rows = get_all_from_wiki()

    for row in all_rows:
        for elem in row[1].split(" // "):
            G.add_edge(row[0], elem)


def sort_on_pagerank(data):
    """ Sort articles based on their PageRank """

    sorted_articles = []
    for article in data:
        cursor = db.cursor()
        cursor.execute("SELECT pagerank FROM pr WHERE title=(?)", (article.title,))
        value = cursor.fetchone()
        article.set_pagerank(value)
        sorted_articles.append(article)
    return sorted(sorted_articles, key=lambda x: x.get_pagerank(), reverse=True)
