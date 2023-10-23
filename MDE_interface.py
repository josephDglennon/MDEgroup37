
# ------------------------- [RECORD AUDIO/SIGNAL INPUT] ------------------------- 
'''
Manages the microphone and any inputs relevant to the recording of a data sample
'''
class Input():

    '''
    Set up microphone and trigger
    - set pins/ports and what ever needs to be done
    '''
    def __init__(self):
        return

    '''
    Begin recording data from inputs to a csv file or python table
    '''
    def start_recording(self):
        return
    
    '''
    Stop recording sample
    '''
    def stop_recording(self):
        return
    
    '''
    Return the tabulated data
    Raise exception if currently recording or if data is otherwise unavailable
    '''
    def get_data(self):
        return

# ------------------------- [PROCESS RAW DATA] ------------------------- 
'''
Processes raw data and produces a new CSV or other type of output object
representing the raw input alongside a 'damage channel'

For example, a colum for 'input signal amplitude vs time' with a column
for 'probable damage vs time'

Statistical probability of damage incurred at time = x would be a good way to 
represent our output data
'''
class Processor():

    '''
    Processor class creates a processed_data object when called
    '''
    def __call__(self, raw_data):

        decomposed_data = self.__decompose(raw_data)
        return self.__process(decomposed_data)
    
    '''
    Deconstruct the raw audio into usable components such as Power, Frequencies, Etc.
    What ever useful components whe can devise to disposition the sample
    '''
    def __decompose(self, raw_data):

        power = []
        frequencies = []
        trigger_signal = []

        decomposed_data = [
            power,
            frequencies,
            trigger_signal # definitely required for processing
        ]

        return decomposed_data
    
    '''
    Return a table/csv object representing our raw data alongside our annotations and any
    additional channels devised to indicate damage recieved by the UAS

    May be done through a pure math, 'hardcoded' approach or through a teachable machine-learning 
    depending on which implementation proves most doable and most robust
    '''
    def __process(self, data_components):
        return

# ------------------------- [Storage] -------------------------
'''
Manages the database or other storage mechanism we decide to implement
'''
class DataBase():

    '''
    Create and add a new entry to the database
    '''
    def save_new_entry(data):
        return
    
    '''
    Remove an entry from database
    '''
    def delete_entry(self, identifier):
        return

    '''
    Return a list of identifiers representing the entries thusfar recorded
    '''
    def get_entries(self):
        return  
    
    '''
    Return the data associated with an entry
    '''
    def get_entry(self, identifier):
        return

# ------------------------- [Device API and Controller] -------------------------
'''
Main controls for device
'''
class Controller():

    '''
    Setup component objects
    '''
    def __init__(self):

        self.input_controller = Input()
        self.processor = Processor()
        self.database = DataBase()
    
    '''
    Initiate new recording 
    '''
    def start_new_recording(self):

        self.input_controller.start_recording()

    '''
    Mark the end of a sample recording, process the sample, and save to database
    '''
    def end_recording(self):

        self.input_controller.stop_recording()
        recording = self.input_controller.get_data()
        processed_data = self.processor(recording)
        self.database.save_new_entry(processed_data)

    '''
    Output a table of entries thusfar collected in the decided upon interface,
    give a rough synoposis/summary of each entry based on diagnosis
    '''
    def list_entries(self):
        return
    
    '''
    Present a specific entry in a human visualizable form with all associated data,
    annotations, and disposition
    '''
    def view_entry(indentifier):
        return

# ------------------------- [Interface] -------------------------
'''
The visible component of the device. Whether we decide upon gui, terminal, etc, much 
of this module is TBD
'''
class Application():
    def __init__(self):
        self.device_controller = Controller()

# ------------------------- [Start Device] -------------------------
def main():

    app = Application()
    app.start()

if __name__ == '__main__':
    main()