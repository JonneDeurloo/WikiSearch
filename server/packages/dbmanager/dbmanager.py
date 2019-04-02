"""

This folder contains all the different databases.

Connection to a databse can be done by simply calling the 
create_connection() function with the database name as parameter.

"""

import os
import sqlite3
from sqlite3 import Error


def create_connection(db_name):
    """ Return a database connection to an SQLite database """

    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        db_path = os.path.join(dir_path, f"{db_name}.db")
        return sqlite3.connect(db_path)
    except Error as e:
        print(e)


def table_exists(db, name):
    """ Check if table exists """
    cursor = db.cursor()
    cursor.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name}'")
    table = cursor.fetchone()
    return table != None


def close_connection(db):
    """ Close a database connection """

    db.close()
