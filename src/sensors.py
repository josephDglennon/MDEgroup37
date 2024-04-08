
import pyfirmata
import settings
import time
import sys
import numpy as np
import threading
import sounddevice
import traceback
from storage import DmgData
from pyfirmata import util
from queue import Queue
from threading import Thread, Event
from scipy.signal import resample

class Recorder:

    def __init__(self):
        try:
            self.trigger_recorder = TriggerRecorder(
                port=settings.get_setting('trigger_port'),
                pin=settings.get_setting('trigger_pin')
            )
        except Exception as e:
            print('Error setting up trigger recorder. Ensure device is attached correctly.')
            print(e)
            return None

        try:
            self.audio_recorder = AudioRecorder(
                device_id=int(settings.get_setting('audio_device_id'))
            )
        except Exception as e:
            print('Error setting up audio recorder.')
            print(e)
            return None

    def start_recording(self):
        self.trigger_recorder.start_recording()
        self.audio_recorder.start_recording()

    def stop_recording(self):
        self.trigger_recorder.stop_recording()
        self.audio_recorder.stop_recording()

    def get_data(self):

        # get data
        tsr, tdata = self.trigger_recorder.get_data()
        asr, adata = self.audio_recorder.get_data()

        # resample to match sample length
        tdata, adata, csr = match_signals(tdata, tsr, adata, asr)

        # verify nothing crazy happened
        assert csr == max(tsr, asr)
        assert len(tdata) == len(adata)

        # convert trigger signal to binary
        b_tdata = []
        for value in tdata:
            if value:
                value = value * 1023
                if value < 300:
                    value = 0
                else:
                    value = 1
            else:
                value = 0
            b_tdata.append(value)


        # pack data and return
        out_data = DmgData()
        out_data.audio_data = np.array(adata)
        b_tdata = np.array(b_tdata)
        b_tdata = b_tdata.reshape(-1, 1)
        out_data.trigger_data = b_tdata
        out_data.sample_rate = csr

        return out_data

class AudioRecorder():
    def __init__(self, device_id: int):

        self._device_id = device_id
        device_info = sounddevice.query_devices(self._device_id)
        self._sample_rate = int(device_info['default_samplerate'])
        self._channels = 2

        self._audio_blocks = []

        def audio_callback(indata, frames, time, status):
            """callback for consumption of audio data from stream"""

            if status:
                print(status, file=sys.stderr)

            self._audio_blocks.append(indata.copy())

        self._audio_stream = sounddevice.InputStream(
            samplerate=self._sample_rate, 
            device=self._device_id,
            channels=self._channels,
            callback=audio_callback)
        
        self._is_recording = False
        
    def start_recording(self):
        if not self._is_recording:
            self._audio_blocks = []
            self._is_recording = True
            self._audio_stream.start()

    def stop_recording(self):
        if self._is_recording:
            self._is_recording = False
            self._audio_stream.stop()

    def get_data(self):
        if self._is_recording:
            raise Exception('Cannot acquire data, recording in progress.')
        else:
            outdata = np.concatenate(self._audio_blocks)
            return self._sample_rate, outdata
        
def get_audio_devices():
    pass




class TriggerRecorder():
    def __init__(self, port: str, pin: str):

        self.thread_output_queue = Queue()
        self.recorder_thread = _TriggerRecorder(port, pin, self.thread_output_queue)
        self.recorder_thread.start()
        self.raw_data = None

    def start_recording(self):
        self.raw_data = None
        self.recorder_thread.start_recording()

    def stop_recording(self):
        self.recorder_thread.stop_recording()
        self.recorder_thread.wait()
        if not self.thread_output_queue.empty():
            self.raw_data = self.thread_output_queue.get()

    def get_data(self):
        if self.raw_data:
            sr = self.raw_data[0]
            values = self.raw_data[1]
            return sr, values
        else:
            raise Exception('Data unavailable.')


class _TriggerRecorder(Thread):

    def __init__(self, port: str, pin: str,
                 out_queue: Queue):
        '''Thread for handling the recording of trigger data.'''

        Thread.__init__(self, daemon=True)

        self._board = pyfirmata.Arduino(port)
        self._analog_pin = self._board.get_pin(pin)
        self._out_queue = out_queue
        self._it = util.Iterator(self._board)
        self._it.start()

        self._samples = []
        self._begin_time = None
        self._end_time = None

        self._stop_event = Event()
        self._start_recording_event = Event()
        self._end_recording_event = Event()
        self._recording_finished = Event()
        self._cleared_event = Event()
        
    def run(self):

        # main loop
        while not self._stop_event.is_set():

            # idle until recording begins
            self._start_recording_event.wait() 
            self._end_recording_event.clear()
            self._recording_finished.clear()
            self._begin_time = time.time()

            # recording loop
            while not self._end_recording_event.is_set():

                # take samples of the trigger signal
                sample = self._analog_pin.read()
                time.sleep(.001)
                self._samples.append(sample)

            # calculate samplerate
            self._end_time = time.time()
            total_time = self._end_time - self._begin_time
            sr = round(len(self._samples) / total_time)

            # package recording onto queue
            output_tuple = (sr, self._samples)
            self._out_queue.put(output_tuple)

            # signal recording is finished
            self._recording_finished.set()

            # reset start flag
            self._start_recording_event.clear()
            
    def start_recording(self):
        '''Clear the output queue and begin recording.'''
        self._cleared_event.clear()
        self.clear_queue()
        self._cleared_event.wait()
        self._start_recording_event.set()

    def stop_recording(self):
        self._end_recording_event.set()

    def wait(self):
        self._recording_finished.wait()

    def clear_queue(self):
        with threading.Lock():
            while not self._out_queue.empty():
                self._out_queue.get()
        self._cleared_event.set()

    def terminate(self):
        self._stop_event.set()


def match_signals(sig_1, sr_1, sig_2, sr_2):
    '''Resample signals to use a common samplerate.

    Will resample the arrays provided by reference into this function. Pass
    a copy into this function to avoid the original array being manipulated.
    
    Parameters
    ----------
    sig_1: ndarray
        Amplitude data for the first signal
    sr_1: int
        Samplerate of the first signal
    sig_2: ndarray
        Amplitude data for the second signal
    sr_2: int
        Samplerate of the seconds signal

    Returns
    -------
    sig_1: ndarray
        First signal adjusted to the common sample rate
    sig_2: ndarray
        Second signal adjusted to the common sample rate
    common_sr: int
        The common samplerate
    '''

    common_sr = max(sr_1, sr_2)

    if len(sig_1) >= len(sig_2):

        sig_2 = resample(sig_2, len(sig_1))

    elif len(sig_1) <= len(sig_2):

        sig_1 = resample(sig_1, len(sig_2))

    return sig_1, sig_2, common_sr


if __name__ == '__main__':

    '''
    rec = Recorder()
    rec.start_recording()
    time.sleep(3)
    rec.stop_recording()
    data = rec.get_data()

    print(data.sample_rate)
    print(data.trigger_data)
    #print(data.audio_data[0:300])
    sounddevice.play(data.audio_data, data.sample_rate)
    sounddevice.wait()
    '''

    '''
    trec = TriggerRecorder('COM4', 'a:0:i')

    trec.start_recording()
    time.sleep(1)
    trec.stop_recording()
    sr, data = trec.get_data()
    print('\n[--Test--]\nsr: ' + str(sr) + '\nlen: ' + str(len(data)))

    trec.start_recording()
    time.sleep(1)
    trec.stop_recording()
    sr, data = trec.get_data()
    print('\n[--Test--]\nsr: ' + str(sr) + '\nlen: ' + str(len(data)))

    trec.start_recording()
    time.sleep(2)
    trec.stop_recording()
    sr, data = trec.get_data()
    print('\n[--Test--]\nsr: ' + str(sr) + '\nlen: ' + str(len(data)))
    '''