import pyaudio
# eventually implement a device manager to pick the desired microphone

def main():
    p = pyaudio.PyAudio()

    for i in range(0, p.get_device_count()):
        print(i, p.get_device_info_by_index(i)['name'])
        return

class HardwareInput():
    '''
    Manages the microphone and any inputs relevant to the recording of a data sample
    '''

    def __init__(self):
        '''
        Set up microphone and trigger
        '''


        return

    
    def start_recording(self):
        '''
        Begin recording data from inputs to a csv file or python table
        '''
        return
    
    
    def stop_recording(self):
        '''
        Stop recording sample
        '''
        return
    
    
    def get_data(self):
        '''
        Return a DmgData object containing the newly recorded data sample
        '''
        return
    
if __name__ == '__main__':
    main()