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


def test_create_tag():

    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()


    db._create_tag(con, 'group1')
    db._create_tag(con, 'group2')

    sql = """
             SELECT value
             FROM tag
          """
    tags = cur.execute(sql).fetchall()

    assert tags[0] == ('group1',)
    assert tags[1] == ('group2',)

    with pytest.raises(db.DatabaseError):
        db._create_tag(con, 'group2')

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))


def test_create_tag_link():

    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    db._create_tag_link(con, 1, 1)
    db._create_tag_link(con, 1, 2)
    db._create_tag_link(con, 1, 3)

    with pytest.raises(db.DatabaseError):
        db._create_tag_link(con, 1, 2)
    
    tag_links = cur.execute("""SELECT tag_id FROM test_tag WHERE test_id=1""").fetchall()

    assert (1,) in tag_links
    assert (2,) in tag_links
    assert (3,) in tag_links

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))


def test_read_linked_tag_ids_by_test_id():

    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    db._create_tag_link(con, 1, 11)
    db._create_tag_link(con, 1, 22)
    db._create_tag_link(con, 1, 33)
    db._create_tag_link(con, 1, 44)
    db._create_tag_link(con, 2, 1)
    db._create_tag_link(con, 2, 2)
    db._create_tag_link(con, 2, 3)

    tag_ids = db._read_linked_tag_ids_by_test_id(con, 1)
    assert len(tag_ids) == 4

    for val in [11,22,33,44]:
        assert val in tag_ids

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))


def test_read_tag_id_by_value():

    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    db._create_tag(con, 'tag1')
    db._create_tag(con, 'tag2')
    db._create_tag(con, 'tag3')

    assert db._read_tag_id_by_value(con, 'tag1') == 1
    assert db._read_tag_id_by_value(con, 'tag2') == 2
    assert db._read_tag_id_by_value(con, 'tag3') == 3

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))


def test_read_tag_value_by_id():

    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    db._create_tag(con, 'tag1')
    db._create_tag(con, 'tag2')
    db._create_tag(con, 'tag3')
    db._create_tag(con, 'tag4')

    assert db._read_tag_value_by_tag_id(con, 1) == 'tag1'
    assert db._read_tag_value_by_tag_id(con, 2) == 'tag2'
    assert db._read_tag_value_by_tag_id(con, 3) == 'tag3'
    assert db._read_tag_value_by_tag_id(con, 4) == 'tag4'

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))


def test_read_all_tag_values():

    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    tag_values = ['tag1', 'tag2', 'tag3', 'tag4']
    for value in tag_values:
        db._create_tag(con, value)

    read_tag_values = db._read_all_tag_values(con)

    assert len(read_tag_values) == 4

    for value in tag_values:
        assert value in read_tag_values

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))


def test_read_test_id_by_name():
    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    db._create_test(con, 'test1', datetime.datetime.now(), '', '')
    db._create_test(con, 'test2', datetime.datetime.now(), '', '')
    db._create_test(con, 'test3', datetime.datetime.now(), '', '')

    assert db._read_test_id_by_name(con, 'test0') == None
    assert db._read_test_id_by_name(con, 'test1') == 1
    assert db._read_test_id_by_name(con, 'test2') == 2
    assert db._read_test_id_by_name(con, 'test3') == 3

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))


def test_read_test_by_id():

    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    time_stamp = datetime.datetime.now()

    test_values = [
        (1, 'test1', time_stamp, 'notes1', 'file1'),
        (2, 'test2', time_stamp, 'notes2', 'file2'),
        (3, 'test3', time_stamp, 'notes3', 'file3'),
        (4, 'test4', time_stamp, 'notes4', 'file4')
    ]

    for value in test_values:
        db._create_test(con, value[1], value[2], value[3], value[4])

    for id in range(1, 5):
        test = db._read_test_by_id(con, id)
        assert test == test_values[id - 1]

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))


def test_update_test():
    pass


def test_update_tag_links():
    pass


def test_delete_tag_link():
    
    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    db._create_tag_link(con, 1, 1)
    db._create_tag_link(con, 1, 2)
    db._create_tag_link(con, 1, 3)
    db._create_tag_link(con, 2, 2)

    db._delete_tag_link(con, 1, 2)

    remaining_tag_links = cur.execute("SELECT test_id, tag_id FROM test_tag").fetchall()

    assert len(remaining_tag_links) == 3
    assert (1,1) in remaining_tag_links
    assert (1,2) not in remaining_tag_links
    assert (1,3) in remaining_tag_links
    assert (2,2) in remaining_tag_links

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))


def test_delete_test_by_id():
    return


def test_delete_tag_links_by_test_id():
    return


def test_delete_tag_links_by_tag_id():
    return


def test_delete_tag_by_id():

    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    db._create_tag(con, 'tag1')
    db._create_tag(con, 'tag2')

    tags = cur.execute("SELECT * FROM tag").fetchone()
    assert tags != None

    db._delete_tag_by_id(con, 1)

    tags = cur.execute("SELECT * FROM tag WHERE value='tag2'").fetchone()
    assert tags != None

    tags = cur.execute("SELECT * FROM tag WHERE value='tag1'").fetchone()
    assert tags == None

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))


""" Test Function Template

def test_():

    db.configure(database_file_path=TEST_DB_FILE_PATH, database_file_name='test.db')
    con = db._connect()
    cur = con.cursor()

    con.close()
    os.remove(os.path.join(TEST_DB_FILE_PATH, 'test.db'))
"""

