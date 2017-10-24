import numpy as np
# import wave as wav
# import struct

def sine_wave(freq, volume, duration, AM=0, sampleRate=44100):
    # create sine wave at frequency, sample rate, (max) volume and duration (secs)
    # optional amplitude modulation (in Hz; default = 0, no modulation)
    m = np.cos((2.0 * np.pi * AM * np.linspace(0, duration, num=sampleRate*duration)) + np.pi)
    s = np.sin(2.0 * np.pi * freq * np.linspace(0, duration, num=sampleRate*duration))
    return np.array((1 + m) * volume * s)

def apply_ramp(wave, onset_duration, offset_duration, sampleRate=44100):
    # create onset and offset ramps using cosine squared
    onset_ramp = np.square(np.cos(np.linspace(np.pi/2, np.pi, onset_duration*sampleRate)))
    offset_ramp = np.square(np.cos(np.linspace(np.pi/2, np.pi, offset_duration*sampleRate)))
    # apply onset ramp in forward
    for (t, x) in enumerate(onset_ramp):
        wave[t] = wave[t] * x
    # apply offset ramp in reverse
    for (t, x) in enumerate(offset_ramp):
        wave[-1 - t] = wave[-1 - t] * x
    return wave

# def write_wavefile(fileName, wave):
#    # output .wav file for given waveform
#    w = wav.open(fileName, 'w')
#    w.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))
#    max_amp = np.max(np.abs(wave))
#    for s in wave:
#        w.writeframes(struct.pack('h', int((s / max_amp) * (32767.0 / 2))))
#        w.writeframes(struct.pack('h', int((s / max_amp) * (32767.0 / 2))))
#    w.close()
#    return
