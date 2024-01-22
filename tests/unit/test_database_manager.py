import pytest
import os
import datetime

import src.database_manager as db

TEST_DB_FOLDER = os.path.join(os.path.dirname(__file__), '.')
TEST_DB_FILE = os.path.join(TEST_DB_FOLDER, 'dmg.db')

def test_initialize_db():
    '''Test that the database is setup properly via its initialize function.'''

    db.DB_FOLDER_PATH = TEST_DB_FOLDER
    db.initialize_db()
    con = db._connect()
    cur = con.cursor()

    # check db file exists in correct location
    assert os.path.isfile(TEST_DB_FILE)

    # check db contains the expected tables
    db_tables = cur.execute('''
                               SELECT name FROM sqlite_master WHERE type='table';
                            ''').fetchall()
    
    test_table_exists = False
    test_file_table_exists = False
    file_type_table_exists = False
    test_tag_table_exists = False
    tag_table_exists = False

    for table in db_tables:
        if table[0] == 'test': test_table_exists = True
        elif table[0] == 'test_file': test_file_table_exists = True
        elif table[0] == 'file_type': file_type_table_exists = True
        elif table[0] == 'test_tag': test_tag_table_exists = True
        elif table[0] == 'tag': tag_table_exists = True

    assert test_table_exists
    assert test_file_table_exists
    assert file_type_table_exists
    assert test_tag_table_exists
    assert tag_table_exists

    # check file type table contains the required default type names
    file_types = cur.execute('''
                                SELECT type FROM file_type
                             ''').fetchall()
    
    input_audio_file_exists = False
    input_trigger_file_exists = False
    output_file_exists = False

    for type in file_types:
        if 'input_audio' in type: input_audio_file_exists = True
        elif 'input_trigger' in type: input_trigger_file_exists = True
        elif 'output' in type: output_file_exists = True

    assert input_audio_file_exists
    assert input_trigger_file_exists
    assert output_file_exists

    con.close()
    os.remove(TEST_DB_FILE)


def test_insert_file_type():

    db.DB_FOLDER_PATH = TEST_DB_FOLDER
    db.initialize_db()
    con = db._connect()
    cur = con.cursor()

    # check that function raises exception when attempting to add a duplicate item to table
    db._insert_file_type(con, 'random_file_type')
    with pytest.raises(db.DatabaseError):
        db._insert_file_type(con, 'random_file_type')

    # check that one and only one copy of 'random_file_type' exists in the table
    types = cur.execute("""SELECT * FROM file_type WHERE type='random_file_type'""").fetchall()
    assert len(types) == 1

    con.close()
    os.remove(TEST_DB_FILE)


def test_get_file_types():

    db.DB_FOLDER_PATH = TEST_DB_FOLDER
    db.initialize_db()
    con = db._connect()
    cur = con.cursor()

    # add some types to the database
    test_types = [
        'type1',
        'type2',
        'type3'
    ]
    for test_type in test_types:
        db._insert_file_type(con, test_type)
    
    # check that all types are found in the database
    types = db._get_file_types(con)
    for test_type in test_types:
        assert test_type in types

    con.close()
    os.remove(TEST_DB_FILE)


def test_insert_test_row():

    db.DB_FOLDER_PATH = TEST_DB_FOLDER
    db.initialize_db()
    con = db._connect()
    cur = con.cursor()

    test_values = [
        ('name1', 'notes1'),
        ('name2', 'notes2'),
        ('name3', 'notes3')
    ]
    for test_value in test_values:
        db._insert_test_row(con, test_value[0], test_value[1])

    # check that entries exist with the correct name and notes values
    sql = """
             SELECT name, notes FROM test 
          """
    dateless_test_rows = cur.execute(sql).fetchall()

    for test_value in test_values:
        assert test_value in dateless_test_rows

    # check that entries retrieved return a datetime object in the 'created' field
    sql = """
             SELECT created FROM test
          """
    timestamps = cur.execute(sql).fetchall()
    for timestamp in timestamps:
        assert type(timestamp[0]) is datetime.datetime

    con.close()
    os.remove(TEST_DB_FILE)


def test_get_test_row_by_id():

    db.DB_FOLDER_PATH = TEST_DB_FOLDER
    db.initialize_db()
    con = db._connect()
    cur = con.cursor()

    test_values = [
        ('name1', 'notes1'),
        ('name2', 'notes2'),
        ('name3', 'notes3')
    ]
    for test_value in test_values:
        db._insert_test_row(con, test_value[0], test_value[1])

    test_row = db._get_test_row_by_id(con, '1')
    assert test_row[1] == 'name1'

    test_row = db._get_test_row_by_id(con, '0')
    assert test_row == None

    con.close()
    os.remove(TEST_DB_FILE)


