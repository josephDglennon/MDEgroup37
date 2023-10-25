import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

# Load the .wav file
sample_rate, audio_data = wavfile.read("testwav.wav")

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