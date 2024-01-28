import pytest
import os
import datetime
import sys

sys.path.append('src')
import database_manager as db
import hardware_input as hi

from numpy import ndarray


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


def test_create_test():

    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    now_date = datetime.datetime.now()

    test_id = db._create_test(con,
                              name='Name1',
                              creation_date=now_date,
                              notes='Notes1',
                              data_file_path='path/to/file1')
    
    assert test_id == 1

    sql = """
             SELECT *
             FROM test
             WHERE id=1
          """
    test_row = cur.execute(sql).fetchone()

    assert test_row == (1, 'Name1', now_date, 'Notes1', 'path/to/file1')

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))


def test_create_new_tag():

    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    db.create_new_tag('group1')
    db.create_new_tag('group2')

    sql = """
             SELECT value
             FROM tag
          """
    tags = cur.execute(sql).fetchall()

    assert tags[0] == ('group1',)
    assert tags[1] == ('group2',)

    with pytest.raises(db.DatabaseError):
        db.create_new_tag('group2')

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))


def test_save_data_to_file():

    data = db.DmgData
    data.sample_rate = 4200
    data.audio_data = ndarray([1,2,3,4,5])
    data.trigger_data = ndarray([6,7,8,9,10])
    data.output_data = ndarray([0,0,0,5,0,0])

    path = os.path.join(TEST_DB_FILE_PATH, 'test_file')
    db._save_test_data_to_file(path, data)

    

""" Test Function Template

def test_():

    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))
"""