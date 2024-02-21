import time
import numpy as np

from hardware_input import HardwareInput  # Replace 'your_script_name' with the actual name of your script

# Define a test function to start and stop recording and check callbacks
def test_recording():
    # Instantiate HardwareInput
    hardware_input = HardwareInput()

    # Start recording
    print("Starting recording...")
    hardware_input.start_recording()

    # Record for a few seconds
    time.sleep(5)  # Record for 5 seconds

    # Stop recording
    print("Stopping recording...")
    hardware_input.stop_recording()

    # Get recorded data
    recorded_data = hardware_input.get_data()

    # Check if data is returned
    if recorded_data is not None:
        print("Audio data recorded:", recorded_data.audio_data.shape)
        print("Trigger data recorded:", recorded_data.trigger_data.shape)
        print("Sample rate:", recorded_data.ard_samplerate)
    else:
        print("No data recorded.")

# Run the test function
test_recording()
