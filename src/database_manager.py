import sqlite3
import os
import datetime


from dataclasses import dataclass, field


_ABSOLUTE_PATH = os.path.dirname(__file__)
DB_FOLDER_PATH = os.path.join(_ABSOLUTE_PATH, '../dmgdevicestorage/db')
_DB_FILE_PATH = os.path.join(DB_FOLDER_PATH, 'dmg.db')


@dataclass
class TestData:
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
    input_audio_file: str
        Path to the file-system save location of the input_audio file recorded for
        this test.
    input_trigger_file: str
        Path to the trigger data input file storage location
    output_file: str
        Path to the output file generated for this test.
    """

    id: int = None
    name: str = None
    notes: str = None
    tags: list[str] = field(default_factory=list)
    creation_date: str = None
    input_audio_file: str = None
    input_trigger_file: str = None
    output_file: str = None


def _connect() -> sqlite3.Connection:
    """Form connection to the database"""

    conn = None
    try:
        conn = sqlite3.connect(_DB_FILE_PATH,
                               detect_types=sqlite3.PARSE_DECLTYPES |
                                            sqlite3.PARSE_COLNAMES)
    except Exception as e:
        print(e)

    return conn


def _initialize_database_tables(conn: sqlite3.Connection):
    """Set up the database tables.
    
    Parameters
    ----------
    conn: sqlite3.Connection, required
        connection to database
    """

    conn.execute("PRAGMA foreign_keys = ON")

    query = ('''
                CREATE TABLE IF NOT EXISTS test (
                    id INTEGER PRIMARY KEY NOT NULL,
                    name TEXT NOT NULL, 
                    created TIMESTAMP NOT NULL,
                    notes TEXT
                );
            ''')
    conn.execute(query)

    query = ('''
                CREATE TABLE IF NOT EXISTS test_file (
                    test_id INTEGER,
                    file_type_id INTEGER,
                    path TEXT NOT NULL,
                    FOREIGN KEY(test_id) REFERENCES test(id),
                    FOREIGN KEY(file_type_id) REFERENCES file_type(id)
                );
            ''')
    conn.execute(query)

    query = ('''
                CREATE TABLE IF NOT EXISTS file_type (
                    id INTEGER PRIMARY KEY,
                    type TEXT
                );
            ''')
    conn.execute(query)

    query = ('''
                CREATE TABLE IF NOT EXISTS test_tag (
                    test_id INTEGER,
                    tag_id INTEGER,
                    FOREIGN KEY(test_id) REFERENCES test(id),
                    FOREIGN KEY(tag_id) REFERENCES tag(id)
                );
            ''')
    conn.execute(query)

    query = ('''
                CREATE TABLE IF NOT EXISTS tag (
                    id INTEGER PRIMARY KEY,
                    value TEXT
                );  
            ''')
    conn.execute(query)

    # add default file types to table
    for type in ('input_audio', 'input_trigger', 'output'):
        _insert_file_type(conn, type)

    conn.commit()


def initialize_db():
    '''Set up the database in the location indicated by DB_FOLDER_PATH.
    
    User must call this function in order to create a database at the desired
    location.
    '''

    global _DB_FILE_PATH
    _DB_FILE_PATH = os.path.join(DB_FOLDER_PATH, 'dmg.db')

    if not os.path.isdir(DB_FOLDER_PATH):
        os.makedirs (DB_FOLDER_PATH)

    if not os.path.isfile(_DB_FILE_PATH):
        conn = _connect()
        _initialize_database_tables(conn)
        conn.close()


def save_test_data(test_data: TestData):
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
    return


class DatabaseError(Exception):
    '''Exception thrown when database operations fail.

    Can be thrown when a sought after value is not found in database, if too
    many occurances of that value or found, or for various other reasons.
    '''

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def retrieve_test_data_by_name(name: str) -> TestData:
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
    data_entry = retrieve_test_data_by_id(test_id)

    return data_entry
 

def retrieve_test_data_by_id(id: str) -> TestData:
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
        test_row = _get_test_row_by_id(id)

        # get all files linked to the provided id
            # file-type, path
        test_files = _get_test_files_by_id(id)

        # get all tags assocated with the provided id
        tags = _get_tags_by_id(id)

        data_entry = TestData
        data_entry.id = int(test_row[0])
        data_entry.name = test_row[1]
        data_entry.creation_date = test_row[2]
        data_entry.notes = test_row[3]

        for file in test_files:
            if file[0] == 'output': data_entry.output_file = file[1]
            elif file[0] == 'input_audio': data_entry.input_audio_file = file[1]
            elif file[0] == 'input_trigger': data_entry.input_trigger_file = file[1]

        data_entry.tags = tags

        return data_entry

    except DatabaseError:
        return None


def list_tests() -> list[TestData]:
    '''Return a list of all entries currently stored in database.
    
    Return
    ------
    data_entries: list[TestData]
        A list containing all unique entries stored in the database.    
    '''
    return


def list_tests_by_tags(tags: list[str]) -> list[TestData]:
    '''Return a list of all entries in database which are linked to any of the
    tags provided.'''
    return


def delete_test_by_id(id: str):
    return


def _insert_file_type(conn: sqlite3.Connection, type: str):
    """Inserts a user specified type into the file_type table.
    
    If the type already exists in the table, raises a DatabaseError.
    """
    cur = conn.cursor()

    sql = """
             SELECT * FROM file_type WHERE (type=?)
          """
    entry = cur.execute(sql, (type,)).fetchone()

    if entry != None: raise DatabaseError('File type already exists in table.')

    sql = """
             INSERT INTO file_type(type)
             VALUES(?)
          """
    cur.execute(sql, (type,))
    conn.commit()


def _get_file_types(conn: sqlite3.Connection):
    '''Return a list of all file types present in the database.'''

    conn.row_factory = lambda cursor, row: row[0]
    cur = conn.cursor()
    sql = """
             SELECT type FROM file_type
          """
    types = cur.execute(sql).fetchall()
    
    return types


def _insert_test_row(conn, name, notes):
    '''Insert a row to the test table and generate a time stamp.'''
    
    cur = conn.cursor()

    # ensure a name was provided
    if name == None: raise DatabaseError('Name must be provided.')

    # check if a test exists with the provided name
    sql = """
             SELECT * FROM test WHERE (name=?)
          """
    existing_rows = cur.execute(sql, (name,)).fetchone()
    if existing_rows != None: raise DatabaseError('A test exists already with this name.')

    # generate time stamp
    timestamp = datetime.datetime.now()

    # insert row
    sql = """
             INSERT INTO test(name, created, notes)
             VALUES(?,?,?) 
          """
    cur.execute(sql, (name, timestamp, notes))


def _get_test_row_by_id(conn, id: str):
    '''Return the row in the test table matching the id provided.
    
    Return None if no rows are found.

    If multiple rows matching the id are found, raise DatabaseError.
    '''

    cur = conn.cursor()
    sql = """
             SELECT * FROM test WHERE (id=?)
          """
    rows = cur.execute(sql, id).fetchall()

    if len(rows) > 1: raise DatabaseError('Multiple test rows found matching the provided id')
    if len(rows) == 0: return None

    row = rows[0]

    return row


def _insert_test_file(conn: sqlite3.Connection, test_id, file_type, file_path):
    '''Add a row to the test_file table with a reference to the relevant test,
    the filetype id, and the path to that file on disc.
    
    Ensures that the filetype exists in the table and that no more than one 
    file of the same type is linked to a distinct test.
    '''
    cur = conn.cursor()

    



def _get_test_files_by_id(id: str):
    return


def _get_tags_by_id(id: str):
    return


def _get_test_id_by_name(name: str):
    return


def main():
    return

initialize_db()
if __name__ == '__main__':
    main()
