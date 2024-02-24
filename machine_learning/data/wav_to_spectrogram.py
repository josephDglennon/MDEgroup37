import os
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

# Function to convert audio file to spectrogram image
def convert_to_spectrogram(input_folder, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Iterate through each .wav file in the input folder
    for file in os.listdir(input_folder):
        if file.endswith(".wav"):
            file_path = os.path.join(input_folder, file)
            output_path = os.path.join(output_folder, os.path.splitext(file)[0] + '.png')
            
            # Load audio file
            y, sr = librosa.load(file_path)
            
            # Generate a spectrogram
            plt.figure(figsize=(10, 4))
            spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
            librosa.display.specshow(librosa.power_to_db(spectrogram, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
            plt.colorbar(format='%+2.0f dB')
            plt.title('Mel Spectrogram')
            plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
            plt.close()
            
            print(f"Converted {file} to {output_path}")

# Example usage
input_folder = "B/test/mic1"
output_folder = "b_spec/test/mic1"
convert_to_spectrogram(input_folder, output_folder)
