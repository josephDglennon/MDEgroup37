import sqlite3
import os
import datetime

from dataclasses import dataclass, field
import dmg_assessment as dmg
from numpy import ndarray


@dataclass
class DmgData:
    """Data class for serving test data between modules"""
    sample_rate: int = field(init=False)
    audio_data: ndarray = field(init=False)
    trigger_data: ndarray = field(init=False)
    output_data: ndarray = field(init=False)


@dataclass
class TestEntry:
    """Data class for keeping test data consolidated between operations.
    
    Attributes
    ----------
    id: int
        The test_id assigned to the sql table(s)' row(s) where this test's data
        is stored (if a save location has been created yet).
    name: str
        The user assigned name/identifier for this test.
    notes: str
        A notes field for the user to save relevant information with a test.
    tags: list[str]
        A list containing all of the tags associated with this test.
    creation_date: str
        String representation of the date and timestamp generated when this test 
        was first saved.
    data_file: str
        Path to file in which test data is saved 
    recording_sample: DataSample
        Recorded audio and trigger data
    """

    id: int = None
    name: str = None
    notes: str = None
    tags: list = None
    creation_date: str = None
    data_file_path: str = None
    data: DmgData = None


class DatabaseManager:
    def __init__(self):
        self._active_test = None

    def get_active_test(self):
        return self._active_test

    def create_new_test(self, name: str) -> TestEntry:
        self._active_test = TestEntry()
        self._active_test.name = name
        self._active_test.creation_date = datetime.datetime.now()

        return self._active_test

    def load_existing_test_by_name(self, name: str) -> TestEntry:
        '''Return a single TestEntry object with a name matching the value provided.
    
        Return 'None' if no entry found.

        Parameters
        ----------
        name: str, required
            The name field to match with existing database entries

        Return
        ------
        data_entry: TestEntry
            An object containing all relevant data for a particular test entry if 
            found or None if entry matching provided name does not exist.
        '''

        test_id = _read_test_id_by_name(name)
        test_entry = self.load_test_by_id(test_id)

        self._active_test = test_entry

        return self._active_test

    def load_test_by_id(self, id: int) -> TestEntry:
        
        con = _connect()
        test_row = _read_test_by_id(con, id)

        test_entry = TestEntry()
        test_entry.id = test_row[0]
        test_entry.name = test_row[1]
        test_entry.creation_date = test_row[2]
        test_entry.notes = test_row[3]
        test_entry.data_file_path = test_row[4]
        
        test_entry.data = _read_data_from_file(test_entry.data_file_path)
        test_entry.tags = _read_linked_tag_ids_by_test_id(con, test_entry.id)

        con.close()

        self._active_test = test_entry
        return self._active_test

    def save_active_test_data(test_entry: TestEntry):
        '''Handles the insertion of new test entries as well as updating of existing
        entries.
        
        Does not allow multiple tests with the same name to be created. Tests with
        the same name will be overwritten with the latest data.
        
        Parameters
        ----------
        test_entry: TestEntry, required
            An object containing data to be saved to database (also used to update
            existing database entries) 
        '''

        con = _connect()
        cur = con.cursor()

        # check if test with name exists
        sql = """
                SELECT id
                FROM test
                WHERE name=?
            """
        existing_test = cur.execute(sql, (test_entry.name,)).fetchone()

        if existing_test == None:
            # insert if no
            test_id = _create_test(con,
                                   name=test_entry.name,
                                   creation_date=test_entry.creation_date,
                                   notes=test_entry.notes,
                                   data_file_path=test_entry.data_file_path)
            test_entry.id = test_id
# todo: generate filepath
            path = None
            _save_test_data_to_file(path=test_entry.data_file_path,
                                    data=test_entry.data,)
            _update_tag_links(test_entry.id, test_entry.tags)

        else:
            # update if yes
            _update_test(con,
                         name=test_entry.name,
                         creation_date=test_entry.creation_date,
                         notes=test_entry.notes,
                         data_file_path=test_entry.data_file_path)
            _save_test_data_to_file(path=test_entry.data_file_path,
                                    data=test_entry.data)
            _update_tag_links(test_entry.id, test_entry.tags)

        con.commit()
        con.close()

    def delete_active_test_entry(self):
        self._active_test = None

        # delete test from test table

        # delete tag links referencing this test

        # delete relevant test files

    def create_new_tag(self, value: str):
        '''Create a new tag with the specified value.
        
        Attempts to add a new tag to the database.
        If tag with specified value already exists, return None.
        Otherwise, add tag and return value.
        '''

        con = _connect()

        try:
            _create_tag(con, value)
            con.commit()
            con.close()
            return value
        
        except DatabaseError:
            con.close()
            return None

        

    
    def list_test_ids(self) -> list[TestEntry]:
        '''Return a list of all entries currently stored in database.
        
        Return
        ------
        data_entries: list[TestData]
            A list containing all unique entries stored in the database.    
        '''
        return


    def list_test_ids_by_tags(self, tags: list[str]) -> list[int]:
        '''Return a list of test ids for all entries in the database which are linked
        to any of the tags provided.'''
        return


    def list_existing_tags(self) -> list[str]:
        '''Return a list of all tag values currently in the database'''
        con = _connect()

        tag_list = _read_all_tag_values(con)

        con.commit()
        con.close()

        return tag_list


    def delete_tag_by_value(self, value: str):
        con = _connect()

        tag_id = _read_tag_id_by_value(con, value)
        _delete_tag_by_id(con, tag_id)

        con.commit()
        con.close()


def _connect() -> sqlite3.Connection:
    """Form connection to the database"""

    conn = None
    try:
        db_file = os.path.join(dmg._database_file_path, dmg._database_file_name)
        con = sqlite3.connect(db_file,
                               detect_types=sqlite3.PARSE_DECLTYPES |
                                            sqlite3.PARSE_COLNAMES)
        
    except Exception as e:
        print(e)

    return con


def _initialize_database_tables(con: sqlite3.Connection):
    """Set up the database tables.
    
    Parameters
    ----------
    con: sqlite3.Connection, required
        connection to database
    """

    con.execute("PRAGMA foreign_keys = ON")

    query = ('''
                CREATE TABLE IF NOT EXISTS test (
                    id INTEGER PRIMARY KEY NOT NULL,
                    name TEXT NOT NULL, 
                    created TIMESTAMP NOT NULL,
                    notes TEXT,
                    data_file_path TEXT
                );
            ''')
    con.execute(query)

    query = ('''
                CREATE TABLE IF NOT EXISTS test_tag (
                    test_id INTEGER,
                    tag_id INTEGER,
                    FOREIGN KEY(test_id) REFERENCES test(id),
                    FOREIGN KEY(tag_id) REFERENCES tag(id)
                );
            ''')
    con.execute(query)

    query = ('''
                CREATE TABLE IF NOT EXISTS tag (
                    id INTEGER PRIMARY KEY,
                    value TEXT
                );  
            ''')
    con.execute(query)

    con.commit()


def configure(files_location=dmg._files_location,
              database_file_path=dmg._database_file_path,
              database_file_name=dmg._database_file_name):
    '''Set up the database in the location indicated by DB_FOLDER_PATH.
    
    User may configure the database at a specified location other than
    the default location.
    '''

    # update settings
    dmg._files_location = files_location
    dmg._database_file_path = database_file_path
    dmg._database_file_name = database_file_name

    # create the specified directories
    if not os.path.isdir(database_file_path):
        os.makedirs(database_file_path)

    # establish database at specified location
    db_file = os.path.join(database_file_path, database_file_name)
    if not os.path.isfile(db_file):
        con = _connect()
        _initialize_database_tables(con)
        con.close()


class DatabaseError(Exception):
    '''Exception thrown when database operations fail.

    Can be thrown when a sought after value is not found in database, if too
    many occurances of that value or found, or for various other reasons.
    '''

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def _save_test_data_to_file(path: str, data: DmgData):
    pass


def _read_data_from_file(path: str) -> DmgData:
    return


# [CRUD]
             
def _create_test(con: sqlite3.Connection,
                 name: str,
                 creation_date: datetime.datetime,
                 notes: str,
                 data_file_path: str) -> int:
    '''Simply inserts data to test table and returns the last row id.
    
    This function is not responsibile for determining whether or not there already
    exists a test with the specified name.
    '''
    
    cur = con.cursor()

    sql = """
             INSERT
             INTO test (name, created, notes, data_file_path)
             VALUES (?,?,?,?)
          """
    
    cur.execute(sql, (name, creation_date, notes, data_file_path))
    
    return cur.lastrowid


def _create_tag(con:sqlite3.Connection, value: str):
    
    cur = con.cursor()
    
    # check if tag exists
    sql = "SELECT * FROM tag WHERE value=?"
    existing_tag = cur.execute(sql, (value,)).fetchone()

    if existing_tag != None: 
        con.close()
        raise DatabaseError('A tag with this value already exists')
        
    # insert a new tag
    sql = """
             INSERT INTO tag(value)
             VALUES(?)
          """
    cur.execute(sql, (value,))


def _create_tag_link(con: sqlite3.Connection, test_id, tag_id):
    
    cur = con.cursor()
    # check if tag link exists already
    sql = """
             SELECT * FROM test_tag
             WHERE test_id=?
             AND tag_id=?
          """
    existing_links = cur.execute(sql, (test_id, tag_id)).fetchone()
    if existing_links != None: raise DatabaseError('A link between the specified test and tag already exists.')

    # add tag link
    sql = """
             INSERT INTO test_tag(test_id, tag_id)
             VALUES(?,?)
          """
    cur.execute(sql, (test_id, tag_id))


def _read_linked_tag_ids_by_test_id(con: sqlite3.Connection, id: int):
    
    con.row_factory = lambda cursor, row: row[0]
    cur = con.cursor()
    sql = """
             SELECT tag_id
             FROM test_tag
             WHERE test_id=?
          """
    existing_tags = cur.execute(sql, (id,)).fetchall()
    con.row_factory = None

    return existing_tags


def _read_tag_id_by_value(con: sqlite3.Connection, value: str):
    cur = con.cursor()
    sql = """
             SELECT id
             FROM tag
             WHERE value=?
          """
    tag = cur.execute(sql, (value,)).fetchone()
    if tag == None: return None
    return tag[0]


def _read_tag_value_by_tag_id(con: sqlite3.Connection, tag_id: int):
    cur = con.cursor()
    sql = """
             SELECT value
             FROM tag
             WHERE id=?
          """
    tag_value = cur.execute(sql, (tag_id,)).fetchone()
    if tag_value == None: return None
    return tag_value[0]


def _read_all_tag_values(con: sqlite3.Connection):

    con.row_factory = lambda cursor, row: row[0]
    cur = con.cursor()
    sql = """
             SELECT value
             FROM tag
          """
    existing_tags = cur.execute(sql).fetchall()
    con.row_factory = None

    return existing_tags


def _read_test_id_by_name(con: sqlite3.Connection, name: str):
    cur = con.cursor()
    sql = """
             SELECT id
             FROM test
             WHERE name=?
          """
    test = cur.execute(sql, (name,)).fetchone()
    if test == None: return None
    return test[0]


def _read_test_by_id(con: sqlite3.Connection, id: int):
    cur = con.cursor()
    sql = """
             SELECT * FROM test
             WHERE id=?
          """
    test = cur.execute(sql, (id,)).fetchone()
    return test


def _update_test(con: sqlite3.Connection,
                 name: str,
                 creation_date: datetime.datetime,
                 notes: str,
                 data_file_path: str):
    '''Update the existing data for the test with the specified name.'''
    return


def _update_tag_links(con: sqlite3.Connection, test_id: int, tag_values: list[str]):
    '''Sync tags in the test_tags table with those given in this function.
    
    Tags found in the database that are not found in the list of tags given
    here are deleted. Tags provided in the tags list which are not yet present
    int the database are inserted.
    '''

    # attempt to add all provided tags to tag via links
    for value in tag_values:
        tag_id = _read_tag_id_by_value(con, value)
        
        # if tag exists: 
        if tag_id:
            # this function handles duplicate tag links
            _create_tag_link(con, test_id, tag_id) 

    # delete tag links from database which are not present in the list provided
    existing_tags = _read_linked_tag_ids_by_test_id(con, test_id)
    for tag_id in existing_tags:

        # check if existing tag value matches one provided
        existing_tag_value = _read_tag_value_by_tag_id(con, tag_id)
        if existing_tag_value not in tag_values:

            # if not, delete the link to it from the database
            _delete_tag_link(con, test_id, tag_id)      


def _delete_tag_link(con: sqlite3.Connection, test_id: int, tag_id: int):
    cur = con.cursor()
    sql = """
             DELETE FROM test_tag 
             WHERE test_id=?
             AND tag_id=? 
          """
    cur.execute(sql, (test_id, tag_id))


def _delete_test_by_id(con: sqlite3.Connection, test_id: int):
    return


def _delete_tag_links_by_test_id(con: sqlite3.Connection, test_id: int):
    return


def _delete_tag_links_by_tag_id(con: sqlite3.Connection, tag_id: int):
    return


def _delete_tag_by_id(con: sqlite3.Connection, tag_id: int):
    cur = con.cursor()
    cur.execute("DELETE FROM tag WHERE id=?", (tag_id,))


def main():
    return

configure()
if __name__ == '__main__':
    main()
