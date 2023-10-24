import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

# Load the .wav file
sample_rate, audio_data = wavfile.read('testwav.wav')

# Ensure the audio is mono (if stereo, take one channel)
if len(audio_data.shape) > 1:
    audio_data = audio_data[:, 0]

# Calculate the time values for the x-axis
time = np.arange(0, len(audio_data)) / sample_rate

# Plot the waveform
plt.figure(figsize=(10, 4))
plt.plot(time, audio_data)
plt.title('Audio Waveform')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.grid(True)
plt.show()
