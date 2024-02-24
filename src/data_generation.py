
import numpy as np
from scipy.signal import resample
from numpy import ndarray
from dataclasses import dataclass, field
from collections import namedtuple


@dataclass
class TestSample:
    '''Dataclass containing the components of a device test sample.

    A test sample consists of an input audio sample and the expected output that the detector
    should produce after successfully analyzing the sample
    
    Properties
    ----------
    audio_wave_form: ndarray
        Amplitude data for the test audio sample
    audio_sample_rate: int
        Sample rate with which the audio was recorded
    expected_output: ndarray
        The 'answer key' of the test sample. The damage detector output should match this
        array assuming the detector successfully assessed the input audio.
    frame_width: int
        The expected output is mapped to the input in chunks (frames) that have a width
        in milliseconds specified by this property. 
        Letting 'length' be the length of the audio recording in ms, 'expected_output' has
        'length' divided by 'frame_width' elements in it.
    '''

    audio_wave_form: ndarray = None
    audio_sample_rate: int = None
    expected_output: ndarray = None
    frame_width: int = 20


class SampleBuilder:

    def __init__(self):
        self.new_sample()

    @property
    def sample(self) -> TestSample:
        sample = self._sample
        self.new_sample()
        return sample

    def new_sample(self, frame_width=20):
        self._sample = TestSample()
        self._sample.frame_width = frame_width

    def append_background_audio(self,
                                audio_data: ndarray,
                                audio_sample_rate: int,
                                length: int,
                                strength: float=1.0,
                                overlap: int=0):
        '''Tile together an audio backing track using a pre-existing audio file and
        append it to the sample in progress.'''

        # match current signal with the sample rate of the signal being added
        self._sample.audio_wave_form, audio_data, common_sample_rate = _match_signals(self._sample.audio_wave_form,
                                                                                      self._sample.audio_sample_rate,
                                                                                      audio_data,
                                                                                      audio_sample_rate)
        self._sample.audio_sample_rate = common_sample_rate


    def insert_damage_audio(self,
                            audio_data: ndarray,
                            audio_sample_rate: int,
                            start: int,
                            stop: int,
                            strength: float=1.0,
                            rollon: int=0,
                            rolloff: int=0):
        pass

    def insert_audio(self,
                     audio_data: ndarray,
                     audio_sample_rate: int,
                     start: int,
                     stop: int,
                     strength: float=1.0,
                     rollon: int=0,
                     rolloff: int=0):
        pass

def _match_signals(sig_1, sr_1, sig_2, sr_2):
    '''Resample signals to use a common samplerate.
    
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

    sig_1 = resample(sig_1, int(len(sig_1) * common_sr / sr_1))
    sig_2 = resample(sig_2, int(len(sig_2) * common_sr / sr_2))

    return sig_1, sig_2, common_sr


def main():
    pass

if __name__ == '__main__':
    main()