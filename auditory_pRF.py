import numpy as np
import os
from psychopy import visual, data, prefs, core, event, gui

# get subject info
myDlg = gui.Dlg(title="")
myDlg.addText('Experiment info')
myDlg.addField('Subject:')
myDlg.addField('Session:', 1)
myDlg.addField('Number of Blocks:', 10)
myDlg.addField('TR (secs):', 3)
myDlg.addField('TA (secs):', 1.5)
myDlg.addField('Tone duration (secs):', 0.1)
myDlg.addField('Inter-burst interval (secs):', 0.1)
myDlg.addField('Number of tones in burst:', 5)
# show dialog and wait for OK or Cancel
subj_data = myDlg.show()  
if myDlg.OK:  
    participant = subj_data[0]
    session = subj_data[1]
    nBlocks = subj_data[2]
    TR = subj_data[3]
    TA = subj_data[4]
    t = subj_data[5]
    ibi = subj_data[6]
    nTones = subj_data[7]
else:
    core.quit()
    
# set parameters
outputFile = 'subjs/' + participant + "_auditory_pRF"
conditionsFile = 'subjs/' + participant + "_equated_freqs.csv"
freqs = [88, 125, 177, 250, 354, 500, 707, 1000, 1414, 2000, 2828, 4000, 5657, 8000]
jitter_range = [200, 300] # ms

# add current path to paths
prefs.general['paths'] = ['/Users/theissjd/Documents/Berkeley/Year2/Auditory_pRF']
# import custom code generate_wave
import generate_wave as gw

# load sound lib
from psychopy import sound
sound.Sound(value=100)

# create fixation window
win = visual.Window([1280, 756])
fixation = visual.TextStim(win, text='+')
fixation.draw()
win.flip()

# load volumes from equating frequencies
conditions = data.importConditions(conditionsFile)
sorted_conditions = sorted(conditions, key=lambda k: (k['session'], k['TrialNumber']),
    reverse=True)
sorted_conditions = sorted_conditions[:len(freqs)]

# set trialList
trialList = []
for (i, f) in enumerate(np.random.permutation(freqs)):
    # set volume
    v = [float(k['volume']) for k in sorted_conditions if k['freq'] == f][0]
    # set jitter
    j = np.random.randint(jitter_range[0], jitter_range[1]) * 0.001
    # set random index for test trial
    if np.random.randint(5) == 1:
        idx = np.random.randint(0, nTones)
    else:
        idx = -1
    trialList.append({'freq': f, 'volume': v, 'jitter': j, 'idx': idx})

# set TrialHandler
trials = data.TrialHandler(trialList, nBlocks,
    extraInfo={'participant': participant, 'session': session, 't': t, 
    'ibi': ibi, 'nTones': nTones})

# trial function
def run_trial(freq, volume, jitter, idx, TR=3, TA=1.5, t=0.1, ibi=0.1, nTones=5):
    # if TTL at TA, then wait for TA to finish
    core.wait(TA)
    core.wait(jitter)
    # set stimulus
    wave = gw.sine_wave(freq, volume, t, AM=5)
    stim = sound.Sound(wave)
    # set burst
    burst = range(0, nTones)
    # set add_ibi (convert to ms and get random interval to add before stimulus)
    add_ibi = np.random.randint(10, (ibi * 1000) - 10) * 0.001
    # record trial onset time
    trialOnset = core.getTime()
    # for each tone in burst
    for x in burst:
        if x == idx:
            core.wait(add_ibi)
            stim.play()
            core.wait(stim.getDuration() + ibi - add_ibi)
        else:
            stim.play()
            core.wait(stim.getDuration() + ibi)
    trialOffset = core.getTime()
    iti = TR - TA - jitter - 0.25 
    core.wait(iti)
    # record response
    resp = event.getKeys(keyList=['1'], timeStamped=True)
    # no response
    if len(resp) == 0:
        trials.addData('resp', 0)
        trials.addData('rt', -1)
        if idx > -1:
            print('miss')
            trials.addData('acc', 0)
        else:
            trials.addData('acc', 1)
    else: # response
        trials.addData('resp', resp[0][0])
        trials.addData('rt', resp[0][1]-trialOnset)
        if idx > -1:
            print('hit')
            trials.addData('acc', 1)
        else:
            print('false alarm')
            trials.addData('acc', 0)
    # addData for trial
    if idx > -1:
        trials.addData('add_ibi', add_ibi)
    trials.addData('trialOnset', trialOnset)
    trials.addData('trialOffset', trialOffset)
    trials.addData('iti', iti)

# run trial for random order of frequencies
beginTime = core.getTime()
for trial in trials:
    pulseOnset = event.waitKeys("5", timeStamped=True) # wait for scanner pulse
    trials.addData('pulseOnset', pulseOnset[0][1])
    run_trial(trial['freq'], trial['volume'], trial['jitter'], trial['idx'],
        TR, TA, t, ibi, nTones)
endTime = core.getTime()
trials.addData('beginTime', beginTime)
trials.addData('endTime', endTime)

# save results
if os.path.isfile(outputFile + '.csv'):
    trials.saveAsWideText(outputFile + '.csv', appendFile=True, matrixOnly=True)
else:
    trials.saveAsWideText(outputFile + '.csv', appendFile=False)
win.close()
core.quit()
