import numpy as np
import os
from psychopy import visual, data, prefs, core, gui

# get subject info
myDlg = gui.Dlg(title="")
myDlg.addText('Experiment info')
myDlg.addField('Subject:')
myDlg.addField('Session:', 1)
myDlg.addField('Number of Blocks:', 1)
myDlg.addField('Comparison frequency (Hz):', 1000)
myDlg.addField('Tone duration (secs):', 0.2)
myDlg.addField('Amplitude Modulation (Hz):', 5)
myDlg.addField('Inter-stimulus interval (secs):', 0.5)
# show dialog and wait for OK or Cancel
subj_data = myDlg.show()  
if myDlg.OK:  
    participant = subj_data[0]
    session = subj_data[1]
    nBlocks = subj_data[2]
    base_freq = subj_data[3]
    duration = subj_data[4]
    AM = subj_data[5]
    isi = subj_data[6]
else:
    core.quit()

# set parameters
outputFile = 'subjs/' + participant + "_equated_freqs"
freqs = [88, 125, 177, 250, 354, 500, 707, 1000, 1414, 2000, 2828, 4000, 5657, 8000]

# add current path to paths
prefs.general['paths'] = ['.']
# import custom code generate_wave
import generate_wave as gw

# load sound lib
from psychopy import sound
from psychopy import event
sound.Sound(value=100)

# create fixation window
win = visual.Window([1280, 756])
fixation = visual.TextStim(win, text='+')
fixation.draw()
win.flip()

# function to equate volumes
def equate_volume(base_freq, base_volume, freq, volume, duration=0.2, isi=0.5):
    resp = ['']
    # generate base_wave
    base_wave = gw.sine_wave(base_freq, volume, duration, AM=AM)
    base_wave = gw.apply_ramp(base_wave, 0.01, 0.01)
    # randomize comparison volume
    if base_freq == freq and base_freq > 0:
        trials.addData('volume', volume)
        return volume
    # generate freq_wave
    freq_wave = gw.sine_wave(freq, volume, duration, AM=AM)
    freq_wave = gw.apply_ramp(freq_wave, 0.01, 0.01)
    # set switch indicators and volume changes
    s = inc = dec = 0
    d = 0.25
    while (resp[0] != '3' and base_freq==0) or s < 4:
        # set base_freq and freq
        stim1 = sound.Sound(base_wave)
        stim2 = sound.Sound(volume*freq_wave)
        # random presentation order
        order = np.random.randint(2)
        # pre isi
        core.wait(isi)
        # if no base_freq, play stim2
        if base_freq == 0:
            stim2.play()
            core.wait(stim2.getDuration())
        elif order == 0:
            # play base_freq then freq
            stim1.play()
            core.wait(stim1.getDuration() + isi)
            stim2.play()
            core.wait(stim2.getDuration())
        else:
            # play freq then base_freq
            stim2 = sound.Sound(volume*freq_wave)
            stim2.play()
            core.wait(stim2.getDuration() + isi)
            stim1.play()
            core.wait(stim1.getDuration())
        # wait for response
        resp = event.waitKeys(['1','2','3'])
        # break if response 3 or 4 switches
        if (resp[0] == '3' and base_freq == 0) or s > 3:
            break
        elif base_freq == 0: # increase or decrease
            if resp[0] == '1':
                volume += 0.1
            elif resp[0] == '2':
                volume -= 0.1
        elif int(resp[0])-1 == order: # chose base (increase)
            volume += d
            inc = 1
        elif int(resp[0])-1 != order: # chose freq (decrease)
            volume -= d
            dec = 1
        # ensure volume not below 0
        if volume <= 0.0:
            volume = 0.1
        # check for switches
        if inc == dec == 1 and base_freq > 0:
            s += 1
            d -= 0.05
            inc = dec = 0
    # add volume
    if base_freq > 0:
        trials.addData('volume', volume)
    return volume

# adjust volume
base_volume = equate_volume(0, 1.0, base_freq, 1.0, duration, isi)

# set trialList
trialList = []
for f in freqs:
    trialList.append({'freq': f})

# set TrialHandler
trials = data.TrialHandler(trialList, nBlocks,
    extraInfo={'participant': participant, 'session': session, 'base_freq': base_freq,
    'base_volume': base_volume})

# for each frequency, equate with base_freq
beginTime = core.getTime()
for trial in trials:
    equate_volume(base_freq, base_volume, trial['freq'], base_volume, duration, isi)
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
