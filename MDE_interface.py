import numpy as np
from matplotlib import pyplot as plt
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
############################################
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

# Plot the frequency content
plt.figure(figsize=(10, 6))
plt.plot(frequencies, fft_result)
plt.title("Frequency Content of Audio File")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)
plt.xlim(0, sample_rate / 2)  # Only display the positive frequencies (up to Nyquist)
plt.show()