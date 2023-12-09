import sqlite3
import os

from dataclasses import dataclass, field


ABSOLUTE_PATH = os.path.dirname(__file__)
DB_FOLDER_PATH = os.path.join(ABSOLUTE_PATH, '..\dmgdevicestorage\db')
DB_FILE_PATH = os.path.join(DB_FOLDER_PATH, 'dmg.db')

if not os.path.isdir(DB_FOLDER_PATH):
    os.makedirs (DB_FOLDER_PATH)


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

def retrieve_test_data_by_name(name: str):
    return


def _connect() -> sqlite3.Connection:
    """Form connection to the database"""

    conn = sqlite3.connect(DB_FILE_PATH)

    return conn


def _initialize_database(conn: sqlite3.Connection):
    """Set up the database tables according to schema
    
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
                    created TEXT NOT NULL
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

    conn.commit()


if not os.path.isfile(DB_FILE_PATH):
    conn = _connect()
    _initialize_database(conn)
    conn.close()


def main():
    return


if __name__ == '__main__':
    main()