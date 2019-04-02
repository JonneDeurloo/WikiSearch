from ..dbmanager import dbmanager as DBM

import csv
import os


def create_connection():
    """ Create a database connection to an SQLite database """

    global db

    db = DBM.create_connection('wiki')


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
			text 		TEXT)
	    ''')
    db.commit()


def create_wiki():
    """ Build the Wiki table """

    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(
        dir_path, '..\\common\\dataset\\enwiki-20190301\\firstline.csv')

    with open(file_path, encoding="utf8") as csvfile:
        firstLineReader = csv.DictReader(csvfile, delimiter=',')
        insert_db = []

        for line in firstLineReader:
            title = tuple(line.values())[0]
            text = get_first_characters(tuple(line.values())[1], 200)
            insert_db.append((title, text))

        cursor = db.cursor()
        cursor.executemany(
            '''INSERT INTO wiki(title, text) VALUES(?,?)''', insert_db)
        db.commit()


def get_first_characters(text, size):
    """ Get first n characters of a string. """

    text = text[:size]
    last = text[-1:]

    while last != ' ':
        text = text[:-1]
        last = text[-1:]

    return text + '...'
