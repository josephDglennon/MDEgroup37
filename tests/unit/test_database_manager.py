import pytest
import os
import datetime

import src.database_manager as db

TEST_FOLDER = os.path.dirname(__file__)
TEST_DB_FILE_PATH = os.path.join(TEST_FOLDER, './testdb')

def test_initialize_db():
    '''Test that the database is setup properly via its initialize function.'''

    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    # check db file exists in correct location
    db_path = os.path.join(TEST_DB_FILE_PATH, 'test.db')
    assert os.path.isfile(db_path)

    # check db contains the expected tables
    db_tables = cur.execute('''
                               SELECT name FROM sqlite_master WHERE type='table';
                            ''').fetchall()

    test_values = [
        ('test',),
        ('test_tag',),
        ('tag',)
    ]

    for value in test_values:
        assert value in db_tables

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))

'''
def test_insert_test_row():

    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    # test

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))


def test_get_test_row_by_id():

    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    # test

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))


def test_insert_into_test_file():
    
    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    # test

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))


'''