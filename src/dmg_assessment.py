
import os
from dataclasses import dataclass


_ABSOLUTE_PATH = os.path.dirname(__file__)
_DEFAULT_DATABASE_FILE_NAME = 'dmg.db'
_DEFAULT_DATABASE_FILE_PATH = os.path.join(_ABSOLUTE_PATH, '../dmgdevicestorage/db')
_DEFAULT_FILES_LOCATION = os.path.join(_ABSOLUTE_PATH, '../dmgdevicestorage/files')

_database_file_name = _DEFAULT_DATABASE_FILE_NAME
_database_file_path = _DEFAULT_DATABASE_FILE_PATH
_files_location = _DEFAULT_FILES_LOCATION


def main():
    pass

if __name__ == '__main__':
    main()