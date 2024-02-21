import time
import matplotlib.pyplot as plt
from hardware_input import HardwareInput
import numpy as np

def plot_data(audio_data, trigger_data, elapsed_time, audio_downsample_factor=50):
    # Generate time axis
    audio_downsampled = audio_data[::audio_downsample_factor]
    time_axis = np.linspace(0, elapsed_time, len(audio_downsampled))
    time_axis2 = np.linspace(0, elapsed_time, len(trigger_data))
    
    # Plot audio data
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(time_axis, audio_downsampled)
    plt.title('Audio Data')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    
    # Plot trigger data
    plt.subplot(2, 1, 2)
    plt.plot(time_axis2, trigger_data)
    plt.title('Trigger Data')
    plt.xlabel('Time (s)')
    plt.ylabel('Value')
    
    plt.tight_layout()
    plt.show()

def main():
    hardware_input = HardwareInput()
    hardware_input.start_recording()
    print("Recording started...")
    time.sleep(10)  # Recording for 10 seconds
    hardware_input.stop_recording()
    print("Recording stopped.")
    
    # Get the data
    data = hardware_input.get_data()
    
    # Plot the data
    plot_data(data.audio_data, data.trigger_data, hardware_input.elapsed_time)

if __name__ == '__main__':
    main()
