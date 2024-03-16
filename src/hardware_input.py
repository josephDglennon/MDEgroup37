import time
import sounddevice
import os
import sys
import numpy
import pyfirmata
import threading

from numpy import ndarray
from dataclasses import dataclass, field

from database_manager import DmgData

from database_manager import DmgData

# todo: eventually implement a device manager to pick the desired microphone
class AnalogReaderThread(threading.Thread):
    def __init__(self, port):
        super().__init__()
        self.board = pyfirmata.Arduino(port)
        self.it = pyfirmata.util.Iterator(self.board)
        self.it.start()
        self.analog_pin = self.board.get_pin('a:0:i')
        self._stop_event = threading.Event()
        self.analog_values = []

    def stop(self):
        self._stop_event.set()

    def get_analog_values(self):
        return self.analog_values

    def run(self):
        try:
            while not self._stop_event.is_set():
                # Read analog value and store
                value = self.analog_pin.read() * 1023
                if value is not None:
                    if value < 300:
                        value = 0
                    else:
                        value = 1
                else:
                    value = 0
                self.analog_values.append(value)

        except KeyboardInterrupt:
            print("Program ended by user.")
            self.cleanup()

    def cleanup(self):
        # Clean up resources, if necessary
        self.board.exit()

class HardwareInput():
    """Manages the microphone and any inputs relevant to the recording of a data sample"""

    def __init__(self):
        """Set up recorder"""

        self._is_recording = False
        self._audio_blocks = []
        self._highlow_values = []
        self._arduino_thread = None
        self._samplerate = None
        self._ard_samplerate = None
        self.start_time = 5
        self.stop_time = 10
        self.elapsed_time = 0

        self.analog_reader_thread = AnalogReaderThread('COM4')

        def audio_callback(indata, frames, time, status):
            """callback for consumption of audio data from stream"""

            if status:
                print(status, file=sys.stderr)

            self._audio_blocks.append(indata.copy())

        
        self._audio_input_device_ID = 1
        self._device_info = sounddevice.query_devices(self._audio_input_device_ID)
        self._sample_rate = int(self._device_info['default_samplerate'])
        self._channels = 2

        self._audio_stream = sounddevice.InputStream(samplerate=self._sample_rate, device=self._audio_input_device_ID,
                                                      channels=self._channels, callback=audio_callback)

    def start_recording(self):
        """Begin recording data from inputs to ndArray queue"""

        if not self._is_recording:
            self._audio_blocks = []
            self._is_recording = True
            self._audio_stream.start()
            self.analog_reader_thread.start()
            self.start_time = time.time()

    def stop_recording(self):
        """Stop recording sample"""

        if self._is_recording:
            self._is_recording = False
            self._audio_stream.stop()
            self.analog_reader_thread.stop()
            self.stop_time = time.time()
            self.analog_reader_thread.join()
            self._highlow_values = self.analog_reader_thread.get_analog_values()
            self.elapsed_time = self.stop_time - self.start_time

    def get_data(self):
        """Return a SampleData object containing audio array, trigger array, and samplerate"""

        if self._is_recording:
            raise Exception("Recording is still in progress")

        output_data = DmgData()
        output_data.sample_rate = self._sample_rate
        output_data.audio_data = numpy.concatenate(self._audio_blocks)
        output_data.trigger_data = numpy.array(self._highlow_values, dtype=numpy.int32)
        output_data.ard_samplerate = int(output_data.trigger_data.shape[0] / self.elapsed_time)

        return output_data

def main():
    pass
    
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('* exit via interrupt *')
