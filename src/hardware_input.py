import time
import sounddevice
import soundfile
import os
import queue
from numpy import ndarray
from dataclasses import dataclass

# todo: eventually implement a device manager to pick the desired microphone

@dataclass
class SampleData():
    audio_data: ndarray
    trigger_data: ndarray
    sample_rate: int


class HardwareInput():
    '''
    Manages the microphone and any inputs relevant to the recording of a data sample
    '''

    def __init__(self):
        '''
        Set up recorder
        '''
        
        self.audio_input_device = 1
        self.device = sounddevice.query_devices(self.audio_input_device)
        self.sample_rate = self.device['default_samplerate']

        self.is_recording = False
        self.audioQueue = queue.Queue()
        

    
    def start_recording(self):
        '''
        Begin recording data from inputs to ndArray queue
        '''
        self.audioQueue.queue.clear()


        return
    
    
    def stop_recording(self):
        '''
        Stop recording sample
        '''
        return
    
    
    def get_data(self):
        '''
        Return a SampleData object containing audio array, trigger array, and samplerate
        '''
        return
    
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

if __name__ == '__main__':
    main()