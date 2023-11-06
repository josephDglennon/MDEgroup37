import librosa
import librosa.display
import sys
sys.path.append('..')

class SignalProcessor():
    '''
    This class produces a classification/prediction based on the raw data provided to it.

    The signal processor is callable when instantiated and is invoked on a tuple containing raw data from the HardwareInput module to 
    produce an output

    raw_data must be a tuple: () 
    '''

    def __call__(self, raw_data):
        '''
        
        '''
        return
    
    
    def __audio_to_spectrogram(self, raw_data):
        '''
        Create a spectrogram of the input data
        '''
        return
    
    def __process(self, data_components):
        return
    
def main():
    file_path = 'audio_data\drill_motor\Drill_1_Speed_Close_To_Far.wav'
    amplitude, sample_rate = librosa.load(file_path)
    trimmed_amplitude, _ = librosa.effects.trim(amplitude)
    librosa.display.waveshow(trimmed_amplitude, sr=sample_rate)
    
    processor = SignalProcessor()

if __name__ == '__main__':
    main()