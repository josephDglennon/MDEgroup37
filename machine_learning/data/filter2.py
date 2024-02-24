import numpy as np
import matplotlib.pyplot as plt
import librosa.display

# Load an audio file
audio_file = 'B/test/mic1/B_R_PC1_946_ConstructionSite_32_snr=13.925772614704403.wav'
y, sr = librosa.load(audio_file)

# Compute the spectrogram
spectrogram = np.abs(librosa.stft(y))

# Set a narrower threshold for the mask
threshold = 0.2 * np.max(spectrogram)

# Create the mask
mask = (spectrogram > threshold)

# Plot the original spectrogram
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.amplitude_to_db(spectrogram, ref=np.max), sr=sr, x_axis='time', y_axis='log')
plt.colorbar(format='%+2.0f dB')
plt.title('Original Spectrogram')
plt.tight_layout()

# Plot the masked spectrogram
plt.figure(figsize=(10, 4))
librosa.display.specshow(librosa.amplitude_to_db(spectrogram * mask, ref=np.max), sr=sr, x_axis='time', y_axis='log')
plt.colorbar(format='%+2.0f dB')
plt.title('Masked Spectrogram with Narrow Threshold')
plt.tight_layout()

plt.show()
