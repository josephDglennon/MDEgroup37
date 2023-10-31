'''
Manages the microphone and any inputs relevant to the recording of a data sample
'''
class HardwareInput():

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