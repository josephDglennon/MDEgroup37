import sqlite3

from dataclasses import dataclass

class DatabaseManager():
    '''
    Permits access to the device storage system
    '''

    def save_new_entry(data):
        '''
        Create and add a new entry to the database
        '''
        return
    
    def delete_entry(self, identifier):
        '''
        Remove an entry from database
        '''
        return

    def get_entries(self):
        '''
        Return a list of identifiers representing the entries thusfar recorded
        '''
        return  
    
    def get_entry(self, identifier):
        '''
        Return the data associated with an entry
        '''
        return