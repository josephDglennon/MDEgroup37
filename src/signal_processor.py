import librosa
import librosa.display
import sys
import numpy as np

import matplotlib.pyplot as plt
import matplotlib

from scipy import signal
from scipy.io.wavfile import write
from hardware_input import DmgData

sys.path.append('..')

class SignalProcessor():
    """This class produces a classification/prediction based on the raw data provided to it.

    The signal processor is callable when instantiated and is invoked on a DmgData
    object containing raw data from the HardwareInput module to produce an output.
    """

    def __call__(self, raw_data: DmgData):
        """"""
        return
    
    
    def _audio_to_spectrogram(self, raw_data: DmgData):
        """Create a spectrogram of the input data"""

        # todo: generate spectrogram

        visualize_audio(raw_data) # basic visualization of the audio time/frequency domain


        '''S = librosa.feature.melspectrogram(y=raw_data.audio_data, sr=raw_data.sample_rate, 
                                           n_mels=128, fmax=8000)
        
        fig, ax = plt.subplots()
        S_dB = librosa.power_to_db(S, ref=np.max)
        img = librosa.display.specshow(S_dB, x_axis='time',
                                y_axis='mel', sr=raw_data.sample_rate,
                                fmax=8000, ax=ax)
        fig.colorbar(img, ax=ax, format='%+2.0f dB')
        ax.set(title='Mel-frequency spectrogram')'''
        
    
    def _process(self, data_components):
        return
    
def main():
    
    file_path = 'audio_data\drill_motor\Drill_1_Speed_Close_To_Far.wav'
    amplitude, sample_rate = librosa.load(file_path)
    trimmed_amplitude, _ = librosa.effects.trim(amplitude)
    librosa.display.waveshow(trimmed_amplitude, sr=sample_rate)
    plt.show()

    signal_processor = SignalProcessor()

    save_folder = 'output'
    signal_processor.visualize_audio(DmgData(audio_data=trimmed_amplitude, sample_rate=sample_rate),
                                 save_folder=save_folder)


def visualize_audio(raw_data: DmgData):
    """Helper function to visualize an audio signal in the time and frequency domain."""

    sample_rate = raw_data.sample_rate
    audio_data = raw_data.audio_data

    # Check the properties of the audio file
    print("Sample Rate:", sample_rate)
    print("Audio Data Shape:", audio_data.shape)

    # Calculate the Fast Fourier Transform (FFT) of the audio data
    fft_result = np.fft.fft(audio_data)
    fft_result = np.abs(fft_result)  # Take the absolute value to get magnitude

    # Calculate the frequency values corresponding to the FFT result
    num_samples = len(fft_result)
    frequencies = np.fft.fftfreq(num_samples, 1.0 / sample_rate)

    # Create subplots to display both the time-domain and frequency-domain graphs
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # Plot the time-domain waveform
    ax1.plot(np.arange(len(audio_data)) / sample_rate, audio_data)
    ax1.set_title("Time-Domain Waveform")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Amplitude")

    # Plot the frequency content
    ax2.plot(frequencies, fft_result)
    ax2.set_title("Frequency Content")
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("Magnitude")
    ax2.grid(True)
    ax2.set_xlim(0, sample_rate / 2)  # Display positive frequencies (up to Nyquist)

    # Adjust spacing between subplots
    plt.tight_layout()

    plt.show()

if __name__ == '__main__':
    main()