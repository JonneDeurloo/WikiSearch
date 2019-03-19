import sqlite3
from sqlite3 import Error

import networkx as nx
import matplotlib.pyplot as plt
import operator
import os

from ..common.article import Article


def create_connection():
    """ Create a database connection to an SQLite database """
    global db

    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        db_path = os.path.join(dir_path, "pr.db")
        db = sqlite3.connect(db_path)
    except Error as e:
        print(e)


def create_table_wiki():
    """ Create wiki table (if not exists) """

    cursor = db.cursor()
    cursor.execute(
        '''
		CREATE TABLE IF NOT EXISTS wiki(
			id 			INTEGER PRIMARY KEY,
			name 		TEXT unique,
			text 		TEXT,
			first		TEXT,
			links 		TEXT)
	    ''')
    db.commit()


def create_table_pagerank():
    """ Create PageRank table (if not exists) """

    cursor = db.cursor()
    cursor.execute(
        '''
		CREATE TABLE IF NOT EXISTS pr(
			id 			INTEGER PRIMARY KEY,
			title 		TEXT unique,
			pagerank	FLOAT)
	    ''')
    db.commit()


def insert_dummy_data():
    wiki = [("A", "first letter alphabet", "The first letter of the alphabet.", "B,C"),
            ("B", "second letter alphabet",
             "The second letter of the alphabet.", "A,C"),
            ("C", "third letter alphabet",
             "The third letter of the alphabet.", "D,A,M,P"),
            ("D", "fourth letter alphabet",
             "The fourth letter of the alphabet.", "E,F,G"),
            ("E", "fifth letter alphabet", "The fifth letter of the alphabet.", "C"),
            ("F", "sixth letter alphabet",
             "The sixth letter of the alphabet.", "C,A,E"),
            ("G", "seventh letter alphabet",
             "The seventh letter of the alphabet.", "D,A"),
            ("H", "eight letter alphabet",
             "The eight letter of the alphabet.", "I,C,M"),
            ("I", "ninth letter alphabet", "The ninth letter of the alphabet.", "M"),
            ("J", "tenth letter alphabet",
             "The tenth letter of the alphabet.", "C,N,Q"),
            ("K", "eleventh letter alphabet",
             "The eleventh letter of the alphabet.", "N,L,A"),
            ("L", "twelfth letter alphabet",
             "The twelfth letter of the alphabet.", "M"),
            ("M", "thirteenth letter alphabet",
             "The thirteenth letter of the alphabet.", "N,O,B"),
            ("N", "fourteenth letter alphabet",
             "The fourteenth letter of the alphabet.", "C,P,Q"),
            ("O", "fifteenth letter alphabet",
             "The fifteenth letter of the alphabet.", "D,F"),
            ("P", "fisixteenthrst letter alphabet",
             "The sixteenth letter of the alphabet.", "G,I,J"),
            ("Q", "seventeenth letter alphabet", "The seventeenth letter of the alphabet.", "C,N,H,P,I")]

    cursor = db.cursor()
    cursor.executemany(
        '''INSERT INTO wiki(name, text, first, links) VALUES(?,?,?,?)''', wiki)
    db.commit()


def get_all_from_wiki():
    """ Get all values from the wiki table """

    cursor = db.cursor()
    cursor.execute('''SELECT name, links FROM wiki''')
    return cursor.fetchall()


def sort_on_pagerank(data):
    """ Sort articles based on their PageRank """

    sorted_articles = []
    for article in data:
        cursor = db.cursor()
        cursor.execute(
            '''SELECT pagerank FROM pr WHERE title=?''', (article.title))
        value = cursor.fetchone()
        article.set_pagerank(value)
        sorted_articles.append(article)
    return sorted(sorted_articles, key=lambda x: x.get_pagerank(), reverse=True)


def create_graph():
    """ Create a directed graph based on the Wikipedia article links"""

    global G
    G = nx.DiGraph()

    all_rows = get_all_from_wiki()

    for row in all_rows:
        for elem in row[1].split(","):
            G.add_edge(row[0], elem)


def create_pagerank():
    """ Build the PageRank table """

    pr = nx.pagerank(G, alpha=0.9)

    cursor = db.cursor()
    cursor.executemany(
        '''INSERT INTO pr(title, pagerank) VALUES(?,?)''', list(pr.items()))
    db.commit()
