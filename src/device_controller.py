from hardware_input import HardwareInput
from signal_processor import SignalProcessor
from database_manager import DatabaseManager


class DeviceController():
    """Main controls for device"""
    
    def __init__(self):
        """Setup component objects"""

        self.input_controller = HardwareInput()
        self.processor = SignalProcessor()
        self.database = DatabaseManager()
    
    
    def start_new_recording(self):
        """Initiate new recording"""

        self.input_controller.start_recording()

    
    def end_recording(self):
        '''
        Mark the end of a sample recording, process the sample, and save to database
        '''

        self.input_controller.stop_recording()
        recording = self.input_controller.get_data()
        #processed_data = self.processor(recording)
        #self.database.save_new_entry(processed_data)


    def list_entries(self):
        '''
        Output a table of entries thusfar collected in the decided upon interface,
        give a rough synoposis/summary of each entry based on diagnosis
        '''
        return
    
    
    def view_entry(indentifier):
        '''
        Present a specific entry in a human visualizable form with all associated data,
        annotations, and disposition
        '''
        return
    