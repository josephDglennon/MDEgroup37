import time
import sounddevice
import soundfile
import os
import sys
import numpy

from numpy import ndarray
from dataclasses import dataclass, field

from database_manager import DmgData

# todo: eventually implement a device manager to pick the desired microphone


class HardwareInput():
    """Manages the microphone and any inputs relevant to the recording of a data sample"""

    def __init__(self):
        """Set up recorder"""

        self._is_recording = False
    
        self._audio_blocks = []

        def callback(indata, frames, time, status):
            """callback for consumption of audio data from stream"""

            nonlocal self

            if status:
                print(status, file=sys.stderr)

            self._audio_blocks.append(indata.copy())

        
        self._audio_input_device_ID = 1
        self._device_info = sounddevice.query_devices(self._audio_input_device_ID)
        self._sample_rate = int(self._device_info['default_samplerate'])
        self._channels = 2 #int(self._device_info['max_input_channels'])

        self._audio_stream = sounddevice.InputStream(samplerate=self._sample_rate, device=self._audio_input_device_ID,
                                    channels=self._channels, callback=callback)
        
    
    def start_recording(self):
        """Begin recording data from inputs to ndArray queue"""

        self._audio_blocks = []
        self._is_recording = True

        self._audio_stream.start()

    
    def stop_recording(self):
        """Stop recording sample"""

        self._is_recording = False

        self._audio_stream.stop()
    
    
    def get_data(self):
        """Return a SampleData object containing audio array, trigger array, and samplerate"""

        if self._is_recording: raise Exception

        output_data = DmgData()
        output_data.sample_rate = self._sample_rate
        output_data.audio_data = numpy.concatenate(self._audio_blocks)

        return output_data


def main():
    pass
    
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('* exit via interrupt *')
