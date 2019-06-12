import soundfile as sf
import os
import numpy as np

# Zero-pads all the stimuli in some folder so all have the same length as the longest one

rootdir = "C:\\Users\\Isaac\\Audio_files\\Stimuli"
stimuli = ["Speech","TakeFive","Dirac"]

for stimulus in stimuli:

    print("Looking for",stimulus,"files...")

    maxdatalen = 0;

    counter = 0
    for folder, subs, files in os.walk(rootdir):
        for filename in files:
            if ".wav" in filename and stimulus in filename:
                counter = counter + 1
                full_path = os.path.join(folder, filename)
                data, fs = sf.read(full_path)
                datalen = data.shape[0]
                if datalen > maxdatalen:
                    maxdatalen = datalen

    print("Found", counter, "files. Maximum length is",maxdatalen)
    print("Zero-padding...")

    for folder, subs, files in os.walk(rootdir):
        for filename in files:
            if ".wav" in filename and stimulus in filename:
                full_path = os.path.join(folder, filename)
                data, fs = sf.read(full_path)
                datalen = data.shape[0]
                padded_data = np.zeros([maxdatalen])
                padded_data[0:datalen] = data
                sf.write(full_path,padded_data, fs)

    print("Finished zero-padding",stimulus)

print("Finished!")