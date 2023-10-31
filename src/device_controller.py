from hardware_input import HardwareInput
from signal_processor import SignalProcessor
from database_manager import DatabaseManager

'''
Main controls for device
'''
class DeviceController():

    '''
    Setup component objects
    '''
    def __init__(self):

        self.input_controller = HardwareInput()
        self.processor = SignalProcessor()
        self.database = DatabaseManager()
    
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