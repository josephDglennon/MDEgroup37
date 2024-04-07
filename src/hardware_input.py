import time
import sounddevice
import os
import sys
import numpy
import pyfirmata
import threading
import data_generation
import settings

from numpy import ndarray
from dataclasses import dataclass, field
from database_manager import DmgData

# todo: eventually implement a device manager to pick the desired microphone

class AnalogReaderThread(threading.Thread):

    class AnalogReaderException(Exception):
        def __init__(self, port):
            super().__init__()

    def __init__(self, port):
        super().__init__()
        try:
            self.board = pyfirmata.Arduino(port)
            self.analog_pin = self.board.get_pin('a:0:i')
            self.it = pyfirmata.util.Iterator(self.board)
            self.it.start()
            self._stop_event = threading.Event()
            self.analog_values = []

        except:
            print('Analog reader improperly setup.')
            raise self.AnalogReaderException('An issue occured while setting up analog reader. Ensure hardware is connected.')           

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
        self._samplerate = None
        self.start_time = None
        self.stop_time = None
        self.elapsed_time = None

        try:
            self.analog_reader_thread = AnalogReaderThread('COM4')

        except AnalogReaderThread.AnalogReaderException as e:
            #print(e)
            self.analog_reader_thread = None

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
            if self.analog_reader_thread:
                self.analog_reader_thread.start()
                self.start_time = time.time()
            else:
                print('Recording without analog reader.')
            

    def stop_recording(self):
        """Stop recording sample"""

        if self._is_recording:
            self._is_recording = False
            self._audio_stream.stop()

            if self.analog_reader_thread:
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

        if self.analog_reader_thread:

            arduino_sample_rate = int(output_data.trigger_data.shape[0] / self.elapsed_time)
            trigger_data = numpy.array(self._highlow_values, dtype=numpy.int32)

            # resample trigger data so it is same as audio
            res_audio, res_trigger, res_sr = data_generation._match_signals(output_data.audio_data,
                                                                            output_data.sample_rate,
                                                                            trigger_data,
                                                                            arduino_sample_rate)
            output_data.audio_data = res_audio
            output_data.trigger_data = res_trigger
            output_data.sample_rate = res_sr

        return output_data

def main():
    pass
    
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('* exit via interrupt *')
