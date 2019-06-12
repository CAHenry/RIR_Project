import soundfile as sf
import os
import numpy as np
from scipy import signal

# Applies SOS filter to all the stimuli. For instance, to lower the bass reponse in eigenmike recordings

rootdir = "C:\\Users\\Isaac\\Audio_files\\Stimuli"
stimuli = ["Speech","TakeFive","Dirac"] # stimuli to be filtered (usually, all of them)
conditions = ["0OA","1OA","2OA","3OA","4OA","MP"] # conditions to be filtered (usually, ambisonics, SDM and MP)

# Filter: low shelf, gain=-15db, fc=1khz from https://arachnoid.com/BiQuadDesigner/
sos = [0.91451797, -1.70941432, 0.80225341, 1, -1.69240694, 0.73377875]

for stimulus in stimuli:

    print("Applying filter to",stimulus,"files...")

    counter = 0
    for folder, subs, files in os.walk(rootdir):
        for filename in files:
            if ".wav" in filename and stimulus in filename:
                counter = counter + 1
                full_path = os.path.join(folder, filename)
                data, fs = sf.read(full_path)
                data_f = signal.sosfilt(sos,data)
                sf.write(full_path,data_f, fs)

    print("Finished applying filter to", counter, "files")

print("Finished!")