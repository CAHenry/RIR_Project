import PyRIR as rir
import os
import soundfile as sf
import numpy as np
from scipy import signal


# ----------------------------------------------------------------------------------------------------------------------
# Define directory, rooms and techniques
# ----------------------------------------------------------------------------------------------------------------------

library = rir.Room("Library", 1.5, 1.2, 1.5)    # name, rt60, rd_ratio, mic_height, mic_distance
trapezoid = rir.Room("Trapezoid", 0.9, 1.2, 1.2)
rooms = [library, trapezoid]

root_dir = "C:\\Users\\Isaac\\Audio_files_07_08"
#root_dir = "/Users/isaacengel/Documents/Audio_files"
stimuli_dir = os.path.join(root_dir, "Stimuli", "Dry")

apply_filter = False
# Filter: low shelf, g=-15db, fc=1khz from https://arachnoid.com/BiQuadDesigner/
sos = [0.91451797, -1.70941432, 0.80225341, 1, -1.69240694, 0.73377875]

mode = "Dirac1"

max_len_file = 0  # maximum file length after convolving, for zero padding

print("Creating", mode, "stimuli...")

stimuli_pos_vec = [[0], [90], [180], [270], ['bottom'], ['top']]
stimuli_name = ['Dirac.wav']

RVL_4OA = rir.Method("RVL_4OA", 32)
method = RVL_4OA

output_dir = os.path.join(root_dir, "Stimuli_07_08", method.name)
if not os.path.isdir(output_dir):
    print("Creating directory", output_dir, "...")
    os.mkdir(output_dir)

for room in rooms:
    RIR_dir = os.path.join(root_dir, "Impulses_07_08", room.name, "Eigenmike", method.name)
    max_len_RIR = 0

    for stimuli_pos in stimuli_pos_vec:

        stimuli = []

        # stimuli is a Nx2 matrix where each row has the dry audio at index 0 and the corresponding RIR at index 1
        for i in range(len(stimuli_pos)):
            stimulus = os.path.join(stimuli_dir, stimuli_name[i])
            RIR = os.path.join(RIR_dir, room.name + "_" + method.name + "_" + str(stimuli_pos[i]) + "_Impulse.wav")
            stimuli.append([stimulus, RIR])
            temp_rir, fs = sf.read(RIR)
            if temp_rir.shape[0] > max_len_RIR:
                max_len_RIR = temp_rir.shape[0]

        temp_stim, fs = sf.read(stimuli[0][0])

        print("Convolving",method.name, room.name,"...")
        convolved = np.zeros([len(stimuli_pos), method.channels, len(temp_stim) + max_len_RIR - 1])

        for file_ind, files in enumerate(stimuli):
            dry, fs = sf.read(files[0])
            RIR, fs = sf.read(files[1])

            RIR = RIR.T

            if len(RIR.shape) > 1:
                for RIR_ind, LS in enumerate(RIR):
                    if len(LS) < max_len_RIR:
                        padding = np.zeros(max_len_RIR - len(LS))
                        LS = np.concatenate([LS, padding])
                    convolved[file_ind][RIR_ind] = signal.fftconvolve(dry / len(stimuli), LS)
            else: # MP
                if len(RIR) < max_len_RIR:
                    padding = np.zeros(max_len_RIR - len(RIR))
                    RIR = np.concatenate([RIR, padding])
                convolved[file_ind][0] = signal.fftconvolve(dry / len(stimuli), RIR)

        if method.name is not "MP":
            output = np.sum(convolved, 0)
        else:
            output = np.sum(convolved, 1) # This is for MP. Basically it's eliminating the 2nd dimension because
                                          # all the indices other than 0 have all zeros

        if output.shape[1] > max_len_file:
            max_len_file = output.shape[1]

        for ind, channel in enumerate(output):

            if apply_filter:
                channel = signal.sosfilt(sos, channel)

            if max(channel) >= 1:
                print("clipping")
            channel = (channel * (2 ** 15 - 1)).astype(np.int16)
            filename = os.path.join(output_dir, room.name + "_" + method.name + "_Dirac1_" + str(stimuli_pos[0]) + "_" + str(ind) + ".wav")

            sf.write(filename, channel, fs, subtype='PCM_24', format='WAV')

# Zero-pad all the stimuli so all have the same length as the longest one
print("Maximum length is", max_len_file)
print("Zero-padding...")

all_stimuli_dir = os.path.join(root_dir, "Stimuli")

counter = 0
for folder, subs, files in os.walk(all_stimuli_dir):
    for filename in files:
        if ".wav" in filename and mode in filename and method.name in filename:
            counter = counter + 1
            full_path = os.path.join(folder, filename)
            data, fs = sf.read(full_path)
            datalen = data.shape[0]
            padded_data = np.zeros([max_len_file])
            padded_data[0:datalen] = data
            sf.write(full_path, padded_data, fs, subtype='PCM_24', format='WAV')

print("Finished zero-padding", counter, mode, "files.")

print("Finished!")
