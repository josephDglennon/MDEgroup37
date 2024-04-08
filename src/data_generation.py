
import librosa
import time
import numpy as np
import sounddevice as sd
from scipy.signal import resample
from numpy import ndarray
from dataclasses import dataclass, replace


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

    wave_form: ndarray = None
    sample_rate: int = None
    expected_output: ndarray = None
    frame_width: int = 20


class SampleBuilder:

    def __init__(self):
        self.reset()

    def get_sample(self) -> TestSample:

        sample = TestSample()
        sample.sample_rate = self.sample_rate
        sample.wave_form = self.wave_form
        sample.frame_width = self.frame_width
        sample.expected_output = self.expected_output
        return sample

    def reset(self, frame_width=20):

        self.sample_rate = None
        self.wave_form = ndarray((0,))
        self.frame_width = frame_width
        self.expected_output = ndarray((0,))
        

    def append_background_audio(self,
                                audio_data: ndarray,
                                audio_sample_rate: int,
                                length: int,
                                strength: float=1.0):
        '''Tiles together an audio backing track using a pre-existing audio file and
        appends it to the sample in progress.
        
        Parameters
        ----------
        audio_data: ndarray
            Array of amplitude data of a source audio signal
        audio_sample_rate: int
            The samplerate for the source audio signal provided
        length: int
            The length in milliseconds desired
        strength: float
            Specify the strength of the source audio relative to its original
            amplitude. A value of 1.0 results in an identical signal.
        '''

        # copy audio data to prevent altering the original
        audio_data = audio_data.copy()

        # match current sample signal with the sample rate of the signal being added
        if (self.sample_rate) and (audio_sample_rate != self.sample_rate):
            _, _, common_sample_rate = _match_signals(self.wave_form,
                                                                                        self.sample_rate,
                                                                                        audio_data,
                                                                                        audio_sample_rate)
            self.sample_rate = common_sample_rate

        elif audio_sample_rate:
            self.sample_rate = audio_sample_rate

        else:
            raise Exception('Something bad just happened')

        # calculate number of samples needed to meet the specified audio length
        target_sample_number = int((float(length) / 1000) * float(self.sample_rate))
        print('target: {}'.format(target_sample_number))

        # calculate max number of tiles of the input audio such that len(result) >= target_sample_number
        num_whole_tiles = int(target_sample_number/len(audio_data))
        remaining_samples = target_sample_number % len(audio_data)

        # scale the input audio
        audio_data = audio_data * strength

        # append whole audio tiles to existing sample
        for i in range (0, num_whole_tiles):
            self.wave_form = np.append(self.wave_form, audio_data)
            self.expected_output = np.append(self.expected_output, ndarray(len(audio_data),))

        # append remaining samples
        self.wave_form = np.append(self.wave_form, audio_data[0:remaining_samples])
        self.expected_output = np.append(self.expected_output, ndarray((remaining_samples,)))


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

    sig_1 = resample(sig_1, int(len(sig_1) * common_sr / sr_1))
    sig_2 = resample(sig_2, int(len(sig_2) * common_sr / sr_2))

    return sig_1, sig_2, common_sr


def main():

    builder = SampleBuilder()
    src_audio_path = 'audio_data\\test_audio\\A\\test\\mic1\\\A_B_MF1_0_ConstructionSite_6_snr=10.926310539796413.wav'
    src_audio, src_samplerate = librosa.load(src_audio_path)
    print('Sample source:\n[INITIAL]')
    print('audio length in samples: ' + str(len(src_audio)))
    print('audio samplerate: ' + str(src_samplerate))

    builder.reset()
    builder.append_background_audio(src_audio,
                                    src_samplerate,
                                    579,
                                    .25)
    sample = builder.get_sample()
    print('FINAL\naudio length in samples: ' + str(len(sample.wave_form)))
    print('samplerate: ' + str(sample.sample_rate))

    
    sd.play(sample.wave_form, sample.sample_rate)
    sd.wait()
    
    duration_seconds = librosa.get_duration(y=sample.wave_form, sr=sample.sample_rate)
    print(duration_seconds)
    duration_seconds = librosa.get_duration(y=sample.expected_output, sr=sample.sample_rate)
    print(duration_seconds)


if __name__ == '__main__':
    main()