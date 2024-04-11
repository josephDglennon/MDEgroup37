
import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray, zeros

def detect_damage_analytically(audio_data: ndarray, audio_sample_rate: int, threshold: float = 0.225) -> ndarray:
    '''Using analytical means, detects occurrences of damage in the sample.
    
    Parameters
    ----------
    audio_data: ndarray
        The raw amplitude data for the audio sample
    audio_sample_rate: int
        The sample rate with which the audio data was recorded
    threshold: float, optional
        The threshold for detecting significant changes in amplitude,
        defaults to 0.225.

    Return
    ------
    dmg_detections: ndarray
        Each value in this array represents the damage status of a 'frame_width' sized
        chunk of the input audio data. Values may be either 1 or 0 representing the 
        presence (or lack thereof) of damage in the sample.
    '''
    # Calculate the number of frames per quarter-second
    frames_per_qtr_sec = int(0.2 * audio_sample_rate)

    # Calculate the index corresponding to the 0.4 second mark
    start_index = int(0.4 * audio_sample_rate)

    # Initialize the damage detections array with zeros for the first second
    dmg_detections = np.zeros(len(audio_data), dtype=int)

    # Detect significant changes in amplitude
    amp_threshold = .002  # Threshold for minimum amplitude to consider
    for i in range(start_index, len(audio_data), frames_per_qtr_sec):
        chunk = audio_data[i:i+frames_per_qtr_sec]
        chunk_mean = np.mean(np.abs(chunk))
        if chunk_mean < amp_threshold:
            dmg_detections[i:i+frames_per_qtr_sec] = 0
            continue
        if i >= start_index + frames_per_qtr_sec:  # Start averaging after 0.4 seconds
            avg_amplitude = np.mean(np.abs(audio_data[start_index:i]))
            if abs(chunk_mean - avg_amplitude) > threshold * avg_amplitude:
                # Timestamp every frame 0.2 seconds after the detected frame
                for j in range(i, min(i + frames_per_qtr_sec, len(audio_data))):
                    dmg_detections[j] = 1

    return dmg_detections


def detect_damage_with_AI(audio_data: ndarray, audio_sample_rate: int) -> ndarray:
    '''Using machine learning, detects occurances of damage in the sample.
    
    Parameters
    ----------
    audio_data: ndarray
        The raw amplitude data for the audio sample
    audio_sample_rate: int
        The sample rate with which the audio data was recorded

    Return
    ------
    dmg_detections: ndarray
        Each value in this array represents the damage status of a 'frame_width' sized
        chunk of the input audio data. Values may be either 1 or 0 representing the 
        presence (or lack thereof) of damage in the sample.
    '''
    return None


def score_damage(dmg_detections: ndarray, trigger_detections: ndarray) -> ndarray:
    '''Analyzes damage detections alongside trigger detections to rate and score the
    occurances of damage in the sample.

    Both arrays must be the same size.

    Damage is classified as follows:

    Class 0: No damage detected AND trigger is in 'off' state
    Class 1: Trigger is in 'on' state AND no damage is detected 
    Class 2: Damage is detected while the trigger is 'on' but ceases once the
    trigger returns to the 'off' state
    Class 3: Damage is detected while the trigger is 'on' and persists for 5
    seconds or less beyond the point when trigger transitions to 'off'
    Class 4: Damage is detected while the trigger is 'on' and persists for 
    longer than 5 seconds beyond the point when trigger transitions to 'off'
    
    Parameters
    ----------
    dmg_detections: ndarray
        An array representing damage occurances on a per-frame basis. A 1 indicates damage
        found to be present within that frame, a 0 indicates the opposite.
    trigger_detections: ndarray
        An array representing detections of a trigger signal on a per-frame basis. 1 indicates
        signal-active, 0 indicates signal-inactive

    Return
    ------
    damage_score: ndarray
        An array which contains the damage rating/score for each frame in the input sample. Values
        in this array may be 0-4 indicating the class of damage present in each sample. 
    '''
    
    if len(dmg_detections) != len(trigger_detections):
        raise ValueError("Arrays must be the same size.")

    damage_score = zeros(len(dmg_detections))

    trigger_on = False
    trigger_on_frame = -1
    trigger_off_frame = -1

    for i in range(len(dmg_detections)):
        if trigger_detections[i] == 1:
            trigger_on = True
            trigger_on_frame = i # i-(5 seconds) ?

        if trigger_detections[i] == 0:
            trigger_on = False
        
        if i >= 2 and trigger_detections[i] == 0 and trigger_detections[i-1] == 1:
            trigger_off_frame = i


        if dmg_detections[i] == 0 and not trigger_on:
            damage_score[i] = 0
        
        elif dmg_detections[i] == 0 and trigger_on:
            damage_score[i] = 1
        elif dmg_detections[i] == 0 and not trigger_on and i - trigger_off_frame > 1: # 1 frame difference
            damage_score[i] = 2
        elif dmg_detections[i] == 1 and not trigger_on and i - trigger_off_frame < 5: # 5 frame difference
            damage_score[i] = 3
        elif dmg_detections[i] == 1 and not trigger_on:
            damage_score[i] = 4
           
    return damage_score

# ----

def plot_dmg_data(audio_data, dmg_data, elapsed_time, audio_downsample_factor=50):
    
    # Generate time axis
    audio_downsampled = audio_data[::audio_downsample_factor]
    time_axis = np.linspace(0, elapsed_time, len(audio_downsampled))
    time_axis2 = np.linspace(0, elapsed_time, len(dmg_data))
    
    # Plot audio data
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(time_axis, audio_downsampled)
    plt.title('Audio Data')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    
    # Plot trigger data
    plt.subplot(2, 1, 2)
    plt.plot(time_axis2, dmg_data)
    plt.title('Damage Detections')
    plt.xlabel('Time (s)')
    plt.ylabel('Value')
    
    plt.tight_layout()
    plt.show()

# ----  
    
def main():
    dmg_detections = np.array([    0, 0, 0, 0, 0, 0, 0, 0, 0,  1,  1, 1, 1, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1,1,1,1,1,1,1,1,1,  1,1,1,1,1,1,1,1,  1,1,1,1,1,1,1,1,  1,1,1,1,1,1,1,1])
    trigger_detections = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0,  1,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0])

    # Call the function
    damage_score = score_damage(dmg_detections, trigger_detections)

    # Print the output
    print(damage_score)

if __name__ == '__main__':
    main()