
import numpy as np
from numpy import ndarray, zeros, insert
from typing import List, Tuple



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


def score_damage(dmg_detections: ndarray, trigger_detections: ndarray, sampleRate: int) -> ndarray:
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
    sampleRate:
        The rate at which the trigger signal is being operated. Needs to be converted to time in order to evaluate.

    Return
    ------
    damage_score: ndarray
        An array which contains the damage rating/score for each frame in the input sample. Values
        in this array may be 0-4 indicating the class of damage present in each sample. 
    '''
    
    if len(dmg_detections) != len(trigger_detections):
        raise ValueError("Arrays must be the same size.")

    damage_score = zeros(len(dmg_detections))
    scoring_difference = 0
    trigger_noise = 0
    trigger_on = False
    trigger_on_frame = -1
    trigger_off_frame = -1

    # Calculate the number of frames corresponding to 5 seconds
    num_frames_5_seconds = sampleRate * 5


    duration_of_test = len(dmg_detections)/sampleRate

    for i in range(len(dmg_detections)):
        if trigger_detections[i] == 1:
            trigger_on = True
            trigger_on_frame = i # i-(5 seconds) ?

        if trigger_detections[i] == 0:
            trigger_on = False
        
        if i >= 2 and trigger_detections[i] == 0 and trigger_detections[i-1] == 1:
            trigger_noise += 1
            trigger_off_frame = i #most recent high to low frame signal from the ttl

        if(trigger_off_frame > 0):
            time_from_off_frame = ((i/sampleRate) - (trigger_off_frame/sampleRate))

        if dmg_detections[i] == 0 and not trigger_on and trigger_off_frame < 0:
            damage_score[i] = 0
        
        elif dmg_detections[i] == 0 and trigger_on:
            damage_score[i] = 1
        elif dmg_detections[i] == 0 and not trigger_on and i - trigger_on_frame > 1 and time_from_off_frame < 5: # 1 frame difference
            damage_score[i] = 2
        elif dmg_detections[i] == 1 and not trigger_on and time_from_off_frame >= 5: # 5 second difference
            damage_score[i] = 4
        elif dmg_detections[i] == 1 and not trigger_on:
            damage_score[i] = 3
        
    if(trigger_noise > 0):
        trigger_noise = 100 - (trigger_noise*2)
        damage_score[0] = trigger_noise   #becasue this number will always be insignificant


    #if there are at least two identical consecutive scorings , range of the score will be packed as a tuple and included in the output. Format: [start_time_ms, end_time_ms, score]
    consecutive_scores = []
    start_index = 0
    for i in range(1, len(damage_score)):
        if damage_score[i] != damage_score[i-1]:
            if start_index != i - 1:
                # Found a range of consecutive scores
                consecutive_scores.append((start_index/sampleRate, i /sampleRate, damage_score[start_index]))
            start_index = i

    # Check for the last range if it continues to the end
    if start_index != len(damage_score) - 1:
        consecutive_scores.append((start_index/sampleRate, duration_of_test, damage_score[start_index]))

    return damage_score, consecutive_scores
    
    # I believe this should work, but I am under the assumption that larger sampling rates would make for much larger length input arrays. Not something I can create by hand in main lol
    

def main():     #test1: 59 element array recorded at a simulated 5 Hz .... 11.8 was expected and is observed
    dmg_detections = np.array([    0, 0, 0, 0, 0, 0, 0, 0, 0,  1,  1, 1, 1, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1,1,1,1,1,1,1,1,1,  1,1,1,1,1,1,1,1,  1,1,1,1,1,1,1,1,  1,1,1,1,1,1,1,1])
    trigger_detections = np.array([0, 0, 0, 0, 0, 0, 0, 1, 1,  1,  0, 1, 1, 0, 0, 1, 0, 1, 1,  0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0])


    dmg_detections2 = np.array([    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    trigger_detections2 = np.array([0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0])
    # Call the function
    damage_score = score_damage(dmg_detections, trigger_detections, 5)

    damage_score2 = score_damage(dmg_detections2, trigger_detections2, 5)

    # Print the output
    print("test1:")
    print(damage_score)
    print("test2:")
    print(damage_score2)

if __name__ == '__main__':
    main()