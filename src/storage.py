import sqlite3
import os
import datetime
import numpy
import taglib
import settings

from scipy.io import wavfile
from dataclasses import dataclass, field
from numpy import ndarray


@dataclass
class DmgData:
    """Data class for serving test data between modules"""
    sample_rate: int = None
    audio_data: ndarray = None
    trigger_data: ndarray = None
    output_data: ndarray = None
    is_processed: bool = False


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
    data_file_path: str
        Path to file in which test data is saved 
    data: DmgData
        Recorded audio and trigger data
    """

    id: int = None
    name: str = None
    notes: str = None
    tags: list = None
    creation_date: datetime.datetime = None
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

        con = _connect()

        test_id = _read_test_id_by_name(con, name)
        test_entry = self.load_existing_test_by_id(test_id)

        self._active_test = test_entry

        con.close()

        return self._active_test

    def load_existing_test_by_id(self, id: int) -> TestEntry:
        
        test_entry = self._load_test_by_id(id)

        self._active_test = test_entry
        return self._active_test

    def save_active_test_data(self):
        '''Creates a new test entry in memory or updates an existing one.
        

        '''

        con = _connect()
        cur = con.cursor()

        test_entry = self._active_test

        # check if test with name exists
        sql = """
                SELECT id
                FROM test
                WHERE name=?
            """
        existing_test = cur.execute(sql, (test_entry.name,)).fetchone()

        if existing_test == None:
            # insert if no test with matching name exists
            test_id, data_file_path = _create_test(con,
                                   name=test_entry.name,
                                   creation_date=test_entry.creation_date,
                                   notes=test_entry.notes)
            test_entry.id = test_id

            if test_entry.data:
                _save_test_data_to_file(path=data_file_path,
                                        data=test_entry.data,)
            _update_tag_links(con, test_entry.id, test_entry.tags)

        else:
            # update if yes
            test_entry.id = _read_test_id_by_name(con, test_entry.name)
            
            _update_test_by_name(con,
                         name=test_entry.name,
                         notes=test_entry.notes)
            
            # overrite data in file
            if test_entry.data:
                _save_test_data_to_file(path=test_entry.data_file_path,
                                        data=test_entry.data)
            
            _update_tag_links(con, test_entry.id, test_entry.tags)

        con.commit()
        con.close()

    def delete_active_test_entry(self):
        '''Deletes only the test entry currently loaded in the DatabaseManager'''
        
        con = _connect()

        # check if test has been assigned an entry in the database tables 
        test_id = _read_test_id_by_name(con, self._active_test.name)

        # delete it
        if test_id:
            self._delete_entry_by_id(test_id)

        # reset manager
        self._active_test = None
        con.commit()
        con.close()

    def delete_test_entry_by_name(self, name: str):
        '''Deletes the specific entry in storage specified'''
        
        con = _connect()

        test_id = _read_test_id_by_name(con, name)
        if test_id: self._delete_entry_by_id(test_id)

        con.commit()
        con.close()

    def discard_active_entry(self):
        self._active_test = None

    def create_new_tag(self, value: str):
        '''Create a new tag with the specified value.
        
        Attempts to add a new tag to the database.
        If tag with specified value already exists, return None.
        Otherwise, add tag and return value.
        '''

        con = _connect()

        try:
            _create_tag(con, value)
        
        except DatabaseError:
            value = None

        con.commit()
        con.close()
        return value
    
    def list_test_ids(self) -> list[int]:
        '''Return a list of all entries currently stored in database.
        
        Return
        ------
        data_entries: list[TestData]
            A list containing all unique entries stored in the database.    
        '''

        con = _connect()
        existing_test_ids = _read_all_test_ids(con)
        return existing_test_ids

    def list_tests_by_tags(self, tags: list[str]) -> list[TestEntry]:
        '''Return a list of tests for all entries in the database which are linked
        to any of the tags provided.'''

        con = _connect()

        tests = []

        if tags:
            for tag in tags:
                # get tests linked to tag
                linked_test_ids = _read_test_ids_linked_to_tag(con, tag)

                # load and add test if not already added
                if linked_test_ids:
                    for id in linked_test_ids:
                        test = self._load_test_by_id(id)
                        if test not in tests: tests.append(test)

        con.close()
        if tests == []: return None
        return tests

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
        _delete_tag_links_by_tag_id(con, tag_id)

        con.commit()
        con.close()

    def _load_test_by_name(self, name: str):

        con = _connect()

        test_id = _read_test_id_by_name(con, name)

        test_entry = None

        if test_id:
            test_entry = self._load_test_by_id(test_id)

        con.close()

        return test_entry

    def _load_test_by_id(self, id: int):

        con = _connect()
        test_row = _read_test_by_id(con, id)
        if test_row == None: return None

        test_entry = TestEntry()
        test_entry.id = test_row[0]
        test_entry.name = test_row[1]
        test_entry.creation_date = test_row[2]
        test_entry.notes = test_row[3]
        test_entry.data_file_path = test_row[4]
        
        test_entry.data = _read_test_data_from_file(test_entry.data_file_path)
        linked_tag_ids = _read_linked_tag_ids_by_test_id(con, test_entry.id)

        if linked_tag_ids:
            test_entry.tags = []
            for id in linked_tag_ids:
                test_entry.tags.append(_read_tag_value_by_tag_id(con, id))

        con.close()
        return test_entry
    
    def _quick_load_test_by_id(self, id: int):

        con = _connect()
        test_row = _read_test_by_id(con, id)
        if test_row == None: return None

        test_entry = TestEntry()
        test_entry.id = test_row[0]
        test_entry.name = test_row[1]
        test_entry.creation_date = test_row[2]
        test_entry.notes = test_row[3]
        test_entry.data_file_path = test_row[4]
        
        #test_entry.data = _read_data_from_file(test_entry.data_file_path)
        linked_tag_ids = _read_linked_tag_ids_by_test_id(con, test_entry.id)

        if linked_tag_ids:
            test_entry.tags = []
            for id in linked_tag_ids:
                test_entry.tags.append(_read_tag_value_by_tag_id(con, id))

        con.close()
        return test_entry
    
    def _delete_entry_by_id(self, test_id):

        con = _connect()

        if (test_id != None):

            test_info = _read_test_by_id(con, test_id)

            # delete the test meta data from database
            _delete_test_by_id(con, test_id)

            # delete tag links referencing this test
            _delete_tag_links_by_test_id(con, test_id)

            # delete relevant test files
            path = test_info[4]

            files_location = os.path.join(settings.get_setting('save_location'), 'files')
            os.remove(os.path.join(files_location, path))
 
        con.commit()
        con.close()
    

def _connect() -> sqlite3.Connection:
    """Form connection to the database"""

    con = None
    try:
        db_file_location = os.path.join(settings.get_setting('save_location'), 'db')
        db_file = os.path.join(db_file_location, settings.get_setting('database_file_name'))
        con = sqlite3.connect(db_file,
                               detect_types=sqlite3.PARSE_DECLTYPES |
                                            sqlite3.PARSE_COLNAMES)
        
    except Exception as e:
        print('<_connect()> connection to database failed')
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


def configure(save_location=settings.get_setting('save_location'),
              database_file_name=settings.get_setting('database_file_name')):
    '''Set up the database in the location indicated by DB_FOLDER_PATH.
    
    User may configure the database at a specified location other than
    the default location.
    '''

    # update settings
    settings.configure_setting('save_location', save_location)
    settings.configure_setting('database_file_name', database_file_name)

    database_file_path = os.path.join(save_location, 'db')
    files_location = os.path.join(save_location, 'files')

    # create the specified directories
    if not os.path.isdir(database_file_path):
        os.makedirs(database_file_path)

    if not os.path.isdir(files_location):
        os.makedirs(files_location)

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
    '''Save the provided data to a .wav file with the name provided by 'path'.

    The .wav file contains channels for audio, trigger, and output data. The audio
    can be comprised of multiple channels and it should be indicated via meta tags
    how many channels are present in the file.

    To indicate whether or not a sample has been processed and contains an output
    channel, a meta tag is added to designate a file 'processed'
    ''' 
    
    if (data.trigger_data is None):
        print('trigger data nonexistent')

    # --------------------------------------------------------------------------------------- TEMPORARY
    #if (data.trigger_data is not ndarray):
    #    data.trigger_data = numpy.zeros((len(data.audio_data),1)) # zero-filled test array

    # check if audio and trigger data is present 
    if (data.audio_data is not None) and (data.trigger_data is not None):

        # determine number of audio channels
        num_audio_channels = len(data.audio_data[0])

        # confirm audio and trigger have the same length
        assert len(data.audio_data) == len(data.trigger_data), 'audio and trigger array size mismatch'

        # combine all data channels into single 'n x channel' array
        wav_channels = numpy.hstack((data.audio_data, data.trigger_data))
        print(wav_channels[0:10])
        if data.is_processed:
            assert data.output_data is not None
            # add output channel if exists
            wav_channels = numpy.append(wav_channels, data.output_data, 1)

            print(wav_channels[0:10])

        # pack wav_channels into a .wav file
        files_location = os.path.join(settings.get_setting('save_location'), 'files')
        full_path = os.path.join(files_location, path)
        wavfile.write(full_path, data.sample_rate, wav_channels)

        # edit meta_tags of the file
        with taglib.File(full_path, save_on_exit = True) as save_file:
            save_file.tags['CHANNELS'] = [str(num_audio_channels)]
            save_file.tags['PROCESSED'] = [str(data.is_processed)]

    else: 
        print('<save_test_data_to_file> Error saving data.')


def _read_test_data_from_file(path: str) -> DmgData:
    '''Extract data from .dmg file and produce a DmgData object.
    
    Assumes the path to be within the dmg._files_location directory. The
    provided path is appended to that variable.
    '''
    
    # check file exists
    files_location = os.path.join(settings.get_setting('save_location'), 'files')
    full_path = os.path.join(files_location, path)
    if not os.path.isfile(full_path): return None

    # extract meta data and wav data from file
    num_channels = 0
    data = DmgData()
    data.sample_rate, wav_channels = wavfile.read(full_path)

    with taglib.File(full_path, save_on_exit = True) as save_file:
        num_channels = int(save_file.tags["CHANNELS"][0])
        is_processed = save_file.tags["PROCESSED"][0]
        if is_processed == 'True': data.is_processed = True
        elif is_processed == 'False': data.is_processed = False
        else: raise Exception('Something really bad just happend. (Read file)')

    # separate channels from wav_data and insert in data object
    data.audio_data = wav_channels[:, 0:(num_channels)]
    data.trigger_data = wav_channels[:, num_channels]
    if data.is_processed:
        data.output_data = wav_channels[:, (num_channels+1)]

    return data

# [CRUD]
             
def _create_test(con: sqlite3.Connection,
                 name: str,
                 creation_date: datetime.datetime,
                 notes: str) -> int:
    '''Simply inserts data to test table and returns the last row id.
    
    This function is not responsibile for determining whether or not there already
    exists a test with the specified name.
    '''
    
    data_file_path = name + '_' + creation_date.strftime("%m%d%Y") + '.dmg'

    cur = con.cursor()

    sql = """
             INSERT
             INTO test (name, created, notes, data_file_path)
             VALUES (?,?,?,?)
          """
    
    cur.execute(sql, (name, creation_date, notes, data_file_path))
    
    return cur.lastrowid, data_file_path


def _create_tag(con:sqlite3.Connection, value: str):
    
    cur = con.cursor()
    
    # check if tag exists
    sql = "SELECT * FROM tag WHERE value=?"
    existing_tag = cur.execute(sql, (value,)).fetchone()

    if existing_tag != None:
        raise DatabaseError('A tag with this value already exists')
        
    # insert a new tag
    sql = """
             INSERT INTO tag(value)
             VALUES(?)
          """
    cur.execute(sql, (value,))

    return cur.lastrowid


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


def _read_data_file_path_by_id(con: sqlite3.Connection, id: int):
    cur = con.cursor()
    sql = """
             SELECT data_file_path
             FROM test
             WHERE id=?
          """
    path = cur.execute(sql, (id,)).fetchone()
    if path == None: return None
    return path[0]


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

    if existing_tags == []: return None

    return existing_tags


def _read_tag_id_by_value(con: sqlite3.Connection, value: str):
    cur = con.cursor()
    sql = """
             SELECT id
             FROM tag
             WHERE value=?
          """
    tag_id = cur.execute(sql, (value,)).fetchone()
    if tag_id == None: return None
    return tag_id[0]


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

    if existing_tags == []: return None

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
    if test == None: return None
    return test


def _read_test_ids_linked_to_tag(con: sqlite3.Connection, tag_value: str):
    '''Produce a list of test ids that are linked to the tag specified.'''

    tag_id = _read_tag_id_by_value(con, tag_value)
    if tag_id == None: return None

    con.row_factory = lambda cursor, row: row[0]
    cur = con.cursor()
    sql = """
             SELECT test_id
             FROM test_tag
             WHERE tag_id=?
          """
    
    linked_tests = cur.execute(sql, (tag_id,)).fetchall()
    con.row_factory = None

    if linked_tests == []: return None
    return linked_tests


def _read_all_test_ids(con: sqlite3.Connection):
    con.row_factory = lambda cursor, row: row[0]
    cur = con.cursor()
    sql = """
             SELECT id
             FROM test
          """
    existing_tests = cur.execute(sql).fetchall()
    con.row_factory = None

    if existing_tests == []: return None
    return existing_tests


def _update_test_by_name(con: sqlite3.Connection,
                         name: str,
                         notes: str,
                         data_file_path: str = None):
    '''Update the existing data for the test with the specified name.
    
    The name and creation_date are set upon creation and are
    not editable.
    '''
    
    cur = con.cursor()
    sql = """
             UPDATE test
             SET notes=?
             WHERE name=?
          """
    
    cur.execute(sql, (notes, name))


def _update_tag_links(con: sqlite3.Connection, test_id: int, tag_values: list[str]):
    '''Sync tags in the test_tags table with those given in this function.
    
    Tags found in the database that are not found in the list of tags given
    here are deleted. Tags provided in the tags list which are not yet present
    int the database are inserted.
    '''

    if tag_values == None: return

    # attempt to add all provided tags to tag via links
    for value in tag_values:
        tag_id = _read_tag_id_by_value(con, value)
        
        # if tag exists: 
        if tag_id:
            # this function handles duplicate tag links
            try:
                _create_tag_link(con, test_id, tag_id)
            except DatabaseError:
                pass # continue if link already exists 

        else:
            # if tag does not already exist, create it and add a link from it to test
            tag_id = _create_tag(con, value)
            _create_tag_link(con, test_id, tag_id)


    # delete tag links from database which are not present in the list provided
    existing_tags = _read_linked_tag_ids_by_test_id(con, test_id)
    if existing_tags:
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
    
    cur = con.cursor()
    sql = """
             DELETE FROM test
             WHERE id=?
          """
    cur.execute(sql, (test_id,))


def _delete_tag_links_by_test_id(con: sqlite3.Connection, test_id: int):
    
    cur = con.cursor()
    sql = """
             DELETE FROM test_tag
             WHERE test_id=?
          """
    cur.execute(sql, (test_id,))


def _delete_tag_links_by_tag_id(con: sqlite3.Connection, tag_id: int):
    
    cur = con.cursor()
    sql = """
             DELETE FROM test_tag
             WHERE tag_id=?
          """
    cur.execute(sql, (tag_id,))


def _delete_tag_by_id(con: sqlite3.Connection, tag_id: int):
    cur = con.cursor()
    sql = """
             DELETE FROM tag
             WHERE id=?
          """
    cur.execute(sql, (tag_id,))


def main():
    return

configure()
if __name__ == '__main__':
    main()
