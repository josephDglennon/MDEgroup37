import pyaudio
import time
import sounddevice 
import soundfile
from scipy.io import wavfile
import os

# todo: eventually implement a device manager to pick the desired microphone

def main():
    
    #sounddevice.default.channels = 1, 5
    #sounddevice.default.device = 5
    print(sounddevice.query_devices())

    this_path = os.path.dirname(__file__)
    print(this_path)
    print('default: ' + str(sounddevice.default.device))
    filename = this_path + "/../audio_data/drill_motor/Drill_1_Speed_Close_To_Far.wav"
    data, fs = soundfile.read(filename)  
    #sounddevice.play(data, fs)
    #time.sleep(1)
    #sounddevice.stop()

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