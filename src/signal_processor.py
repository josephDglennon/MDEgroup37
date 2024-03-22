
import numpy as np
from numpy import ndarray, zeros


def detect_damage_analytically(audio_data: ndarray, audio_sample_rate: int) -> ndarray:
    '''Using analytical means, detects occurances of damage in the sample.
    
    Parameters
    ----------
    audio_data: ndarray
        The raw amplitude data for the audio sample
    audio_sample_rate: int
        The sample rate with which the audio data was recorded

    Return
    ------
    dmg_detections: ndarray
        Each value in this array represents the damage status of a sample
        of the input audio data. Values may be either 1 or 0 representing the 
        presence (or lack thereof) of damage in the sample.
    '''
    pass


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
    pass


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
    
    

def main():
    dmg_detections = np.array([    0, 0, 0, 0, 0, 0, 0, 0, 0,  1,  1, 1, 1, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1,1,1,1,1,1,1,1,1,  1,1,1,1,1,1,1,1,  1,1,1,1,1,1,1,1,  1,1,1,1,1,1,1,1])
    trigger_detections = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0,  1,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0])

    # Call the function
    damage_score = score_damage(dmg_detections, trigger_detections)

    # Print the output
    print(damage_score)

if __name__ == '__main__':
    main()