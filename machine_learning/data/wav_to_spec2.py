import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import torch
from torchaudio.transforms import FrequencyMasking, TimeMasking

class SpectrogramConverter:
    @staticmethod
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
                
                # Apply spectrogram augmentation
                augmented_spec = SpectrogramConverter.spectro_augment(spectrogram)
                
                plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
                plt.close()
                
                print(f"Converted {file} to {output_path}")
    
    @staticmethod
    def spectro_augment(spec, max_mask_pct=0.1, n_freq_masks=1, n_time_masks=1):
        # Check if spec is mono and add a channel dimension if necessary
        if len(spec.shape) == 2:
            spec = np.expand_dims(spec, axis=0)  # Add channel dimension

        # Convert NumPy array to PyTorch tensor
        spec_tensor = torch.tensor(spec)

        _, n_mels, n_steps = spec_tensor.shape
        mask_value = spec_tensor.mean()
        aug_spec = spec_tensor

        freq_mask_param = max_mask_pct * n_mels
        for _ in range(n_freq_masks):
            aug_spec = FrequencyMasking(freq_mask_param)(aug_spec, mask_value)

        time_mask_param = max_mask_pct * n_steps
        for _ in range(n_time_masks):
            aug_spec = TimeMasking(time_mask_param)(aug_spec, mask_value)

        # Convert back to NumPy array before returning
        return aug_spec.numpy()

# Example usage
input_folder = "B/test/mic1"
output_folder = "b_spectrogram"
SpectrogramConverter.convert_to_spectrogram(input_folder, output_folder)
