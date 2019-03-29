import networkx as nx
import csv
import os

from ..dbmanager import dbmanager as DBM
from ..common.wiki_link_extractor import wiki_link_extractor as WLE


def create_connection():
    """ Create a database connection to an SQLite database """

    global db

    db = DBM.create_connection('wiki')


def create_table_pagerank():
    """ Create pagerank table (if not exists) """

    cursor = db.cursor()
    cursor.execute(
        '''DROP TABLE IF EXISTS `pagerank`''')
    cursor.execute(
        '''
		CREATE TABLE IF NOT EXISTS pagerank(
			id 			INTEGER PRIMARY KEY,
			title 		TEXT unique,
			links 		TEXT,
            pagerank    FLOAT DEFAULT 0.0)
	    ''')
    db.commit()


def get_all_links():
    """ Get all links from the pagerank table """

    cursor = db.cursor()
    cursor.execute('''SELECT title, links FROM pagerank''')
    return cursor.fetchall()


def find_links(file):
    """ Build the pagerank table """

    # Define paths
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(
        dir_path, f'..\\common\\dataset\\{file}\\{file}')
    title_path = os.path.join(
        dir_path, f'..\\common\\dataset\\{file}\\article_titles.txt')

    # Extract titles
    titles = []

    with open(title_path, encoding="utf8") as tf:
        for line in tf:
            titles.append(line.replace('\n', ''))

    # Read XML file
    WLE.xml_to_csv(file_path + '.xml')

    # Insert links into database
    with open(file_path + '.csv', encoding="utf8") as csvfile:
        wikireader = csv.DictReader(csvfile, delimiter='?', quotechar='|')
        wiki_insert = []

        for row in wikireader:
            if (len(tuple(row.values())) > 2):
                print(tuple(row.values()))  # Should not happen

            if (tuple(row.values())[0] in titles):
                wiki_insert.append(tuple(row.values()))

        cursor = db.cursor()
        cursor.executemany(
            '''INSERT INTO pagerank(title, links) VALUES(?,?)''', wiki_insert)
        db.commit()


def create_pagerank(dataset):
    """ Add the pagerank to the table """

    if not DBM.table_exists(db, 'pagerank'):
        create_table_pagerank()
        find_links(dataset)

    __create_graph()
    pr = nx.pagerank(G, alpha=0.9)

    cursor = db.cursor()
    cursor.executemany(
        '''UPDATE pagerank SET pagerank = ? WHERE title = ?''', [t[::-1] for t in list(pr.items())])
    db.commit()


def __create_graph():
    """ Create a directed graph based on the Wikipedia article links"""

    global G
    G = nx.DiGraph()

    links = get_all_links()

    for link_row in links:
        for link in link_row[1].split(" // "):
            G.add_edge(link_row[0], link)


def sort_on_pagerank(data):
    """ Sort articles based on their PageRank """

    sorted_articles = []

    for article in data:
        cursor = db.cursor()
        cursor.execute(
            "SELECT pagerank FROM pagerank WHERE title=?", (article.title,))
        value = cursor.fetchone()
        print(article.title, value)
        article.set_pagerank(value[0])
        sorted_articles.append(article)
    return sorted(sorted_articles, key=lambda x: x.get_pagerank(), reverse=True)
