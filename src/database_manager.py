import sqlite3
import os

from dataclasses import dataclass


ABSOLUTE_PATH = os.path.dirname(__file__)
DB_FOLDER_PATH = os.path.join(ABSOLUTE_PATH, '..\dmgdevicestorage\db')
DB_FILE_PATH = os.path.join(DB_FOLDER_PATH, 'dmg.db')

if not os.path.isdir(DB_FOLDER_PATH):
    os.makedirs (DB_FOLDER_PATH)


class DatabaseManager():
    '''
    Permits access to the device storage system
    '''

    def __init__(self):

        self.conn = sqlite3.connect(DB_FILE_PATH)
        initialize_database(self.conn)

        self.conn.execute("PRAGMA foreign_keys = ON")


def initialize_database(conn: sqlite3.Connection):

    query = ('''CREATE TABLE IF NOT EXISTS test (
                id INTEGER PRIMARY KEY NOT NULL,
                name TEXT NOT NULL, 
                created TEXT NOT NULL
            );''')
    conn.execute(query)

    query = ('''CREATE TABLE IF NOT EXISTS test_file (
                test_id INTEGER,
                file_id INTEGER,
                path TEXT,
                FOREIGN KEY(test_id) REFERENCES test(id),
                FOREIGN KEY(file_id) REFERENCES file(id),
                PRIMARY KEY(test_id, file_id)
            );''')
    conn.execute(query)

    query = ('''CREATE TABLE IF NOT EXISTS file (
                id INTEGER PRIMARY KEY,
                type TEXT
            );''')
    conn.execute(query)

    query = ('''CREATE TABLE IF NOT EXISTS test_tag (
                test_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY(test_id) REFERENCES test(id),
                FOREIGN KEY(tag_id) REFERENCES tag(id),
                PRIMARY KEY(test_id, tag_id)
            );''')
    conn.execute(query)

    query = ('''CREATE TABLE IF NOT EXISTS tag (
                id INTEGER PRIMARY KEY,
                value TEXT
            );''')
    conn.execute(query)


def main():
    db_manager = DatabaseManager()

if __name__ == '__main__':
    main()