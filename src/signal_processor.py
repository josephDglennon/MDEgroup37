
import numpy as np
from numpy import ndarray



def detect_damage_analytically(audio_data: ndarray, audio_sample_rate: int, threshold: float = 0.225) -> ndarray:
    '''Using analytical means, detects occurances of damage in the sample.
    
    Parameters
    ----------
    audio_data: ndarray
        The raw amplitude data for the audio sample
    audio_sample_rate: int
        The sample rate with which the audio data was recorded
    frame_length: int
        The desired width of the frame that the output should be mapped to.

    Return
    ------
    dmg_detections: ndarray
        Each value in this array represents the damage status of a 'frame_width' sized
        chunk of the input audio data. Values may be either 1 or 0 representing the 
        presence (or lack thereof) of damage in the sample.
    '''
    # Calculate the number of frames per quarter-second
    frames_per_qtr_sec = int(0.25 * audio_sample_rate)

    # Calculate the mean amplitude for the first second
    avg_amplitude = np.mean(np.abs(audio_data[:frames_per_qtr_sec]))

    # Detect significant changes in amplitude
    dmg_detections = np.zeros(len(audio_data), dtype=int)
    for i in range(0, len(audio_data), frames_per_qtr_sec):
        chunk = audio_data[i:i+frames_per_qtr_sec]
        chunk_mean = np.mean(np.abs(chunk))
        if abs(chunk_mean - avg_amplitude) > threshold * avg_amplitude:
            # Timestamp every frame 0.25 seconds after the detected frame
            for j in range(i, min(i + frames_per_qtr_sec, len(audio_data))):
                dmg_detections[j] = 1

    return dmg_detections


def detect_damage_with_AI(audio_data: ndarray, audio_sample_rate: int, frame_length: int) -> ndarray:
    '''Using machine learning, detects occurances of damage in the sample.
    
    Parameters
    ----------
    audio_data: ndarray
        The raw amplitude data for the audio sample
    audio_sample_rate: int
        The sample rate with which the audio data was recorded
    frame_length: int
        The desired width of the frame that the output should be mapped to.

    Return
    ------
    dmg_detections: ndarray
        Each value in this array represents the damage status of a 'frame_width' sized
        chunk of the input audio data. Values may be either 1 or 0 representing the 
        presence (or lack thereof) of damage in the sample.
    '''
    pass


def score_damage(dmg_detections: ndarray, trigger_detections: ndarray, frame_width: int) -> ndarray:
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
    frame_width: int
        The width of a frame in ms

    Return
    ------
    damage_score: ndarray
        An array which contains the damage rating/score for each frame in the input sample. Values
        in this array may be 0-4 indicating the class of damage present in each frame. 

    '''
    pass
    

def main():
    pass

if __name__ == '__main__':
    main()