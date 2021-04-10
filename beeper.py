import sounddevice as sd
import numpy as np

fs = 44100
volume = 0.5     # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer
duration = 1.0   # in seconds, may be float
#f = 440.0        # sine frequency, Hz, may be float
f = 2500

# generate samples, note conversion to float32 array
samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)

def start_beeping():
    sd.play(samples, blocking=False, loop=True)

def stop_beeping():
    sd.stop()
