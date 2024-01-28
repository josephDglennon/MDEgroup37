import sqlite3
import os
import datetime

from dataclasses import dataclass, field
import dmg_assessment as dmg
from hardware_input import DmgData
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
    data_file: str = None
    input_data_sample: DmgData = None


class DatabaseManager:
    def __init__(self):
        self.active_test = None

    def create_new_test(self) -> TestEntry:
        self.active_test = TestEntry()

        return self.active_test

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

        test_id = _get_test_id_by_name(name)
        test_entry = self.load_test_by_id(test_id)

        return test_entry

    def load_test_by_id(self, id: int) -> TestEntry:
        pass

    def save_active_test_data(test_entry: TestEntry):
        '''Handles the insertion of new test entries as well as updating of existing
        entries.
        
        If the object has an id, update the entry at that id with the data contained
        in the TestData object.
        
        If the object contains no id, create a new entry in the data base and insert 
        all of the relevant data.
        
        Does not allow empty name field and the name entered cannot be the same as the
        name of any existing entries. If the id exists but the name does not match, 
        the name is overwritten for that entry. Other fields are overwritten in the same
        manner if provided fields differ from those which are saved in the database.
        
        Parameters
        ----------
        test_data: TestData, required
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
            _create_test(con,
                         name=test_entry.name,
                         creation_date=test_entry.creation_date,
                         notes=test_entry.notes,
                         data_file_path=test_entry.data_file)
            _save_test_data_to_file(path=test_entry.data_file,
                                    input=test_entry.input_data_sample,
                                    output=test_entry.output_data)
            _update_tag_links(test_entry.id, test_entry.tags)

        else:
            # update if yes
            _update_test(con,
                         name=test_entry.name,
                         creation_date=test_entry.creation_date,
                         notes=test_entry.notes,
                         data_file_path=test_entry.data_file)
            _save_test_data_to_file(path=test_entry.data_file,
                                    input=test_entry.input_data_sample,
                                    output=test_entry.output_data)
            _update_tag_links(test_entry.id, test_entry.tags)

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


def create_new_tag(value: str):

    con = _connect()
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

    con.commit()
    con.close()


def load_test_data_by_name(name: str) -> TestEntry:
    '''Return a single TestData object with a name matching the value provided.
    
    Return 'None' if no entry found.

    Parameters
    ----------
    name: str, required
        The name field to match with existing database entries

    Return
    ------
    data_entry: TestData
        An object containing all relevant data for a particular test entry if 
        found or None if entry matching provided name does not exist.
    '''

    test_id = _get_test_id_by_name(name)
    data_entry = load_test_data_by_id(test_id)

    return data_entry
 

def load_test_data_by_id(id: int) -> TestEntry:
    '''Return a single TestData object with an id matching the value provided.
    
    Collects all data which references the provided id in all tables in the 
    database and packages it into a TestData instance.

    Return 'None' if no entry found.

    Parameters
    ----------
    id: str, required
        The id field to match with existing database entries

    Return
    ------
    data_entry: TestData
        An object containing all relevant data for a particular test entry if 
        found or None if entry matching provided id does not exist.
    '''

    # check that entry exists
    try:
        # get row from test table with matching id 
            # id, name, created, notes
        test_row = _read_test_by_id(id)

        # get all tags assocated with the provided id
        tags = _read_tags_by_test_id(id)

        data_entry = TestEntry
        data_entry.id = int(test_row[0])
        data_entry.name = test_row[1]
        data_entry.creation_date = test_row[2]
        data_entry.notes = test_row[3]
        data_entry.data_file = test_row[4]

        data_entry.tags = tags

        return data_entry

    except DatabaseError:
        return None


def list_test_ids() -> list[TestEntry]:
    '''Return a list of all entries currently stored in database.
    
    Return
    ------
    data_entries: list[TestData]
        A list containing all unique entries stored in the database.    
    '''
    return


def list_test_ids_by_tags(tags: list[str]) -> list[int]:
    '''Return a list of test ids for all entries in the database which are linked
    to any of the tags provided.'''
    return


def list_tags() -> list[str]:
    '''Return a list of all tags currently in the database'''
    return


def delete_tag_by_name(name: str):
    return


def delete_test_by_id(id: int):
    return


# [CRUD]
                
def _create_test(con: sqlite3.Connection,
                 name: str,
                 creation_date: datetime.datetime,
                 notes: str,
                 data_file_path: str) -> int:
    
    cur = con.cursor()

    sql = """
             INSERT
             INTO test (name, created, notes, data_file_path)
             VALUES (?,?,?,?)
          """
    
    cur.execute(sql, (name, creation_date, notes, data_file_path))
    
    return cur.lastrowid


def _create_tag(con:sqlite3.Connection, name: str):
    return


def _read_test_by_id(con: sqlite3.Connection, id: int):
    return


def _read_tags_by_test_id(con: sqlite3.Connection, id: int):
    return


def _read_all_tags(con: sqlite3.Connection):
    return


def _get_test_id_by_name(con: sqlite3.Connection, name: str):
    return


def _read_test_by_id(con: sqlite3.Connection, id: int):
    return


def _update_test(con: sqlite3.Connection,
                 name: str,
                 creation_date: datetime.datetime,
                 notes: str,
                 data_file_path: str):
    return


def _save_test_data_to_file(path: str, input: DmgData, output: ndarray):
    pass


def _update_tag_links(id: int, tags: list[str]):
    pass


def main():
    return

configure()
if __name__ == '__main__':
    main()
