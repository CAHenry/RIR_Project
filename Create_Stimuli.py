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

mode = "TakeFive"
if mode is "TakeFive":
    stimuli_pos = [30, 0, 0, 0, 330]
    stimuli_name = ['Piano.wav', 'Ride.wav', 'Kick.wav', 'Snare.wav', 'Sax.wav']
elif mode is "Dirac":
    stimuli_pos = [30, 0, 0, 0, 330]
    stimuli_name = ['Dirac.wav', 'Dirac.wav', 'Dirac.wav', 'Dirac.wav', 'Dirac.wav']
elif mode is "Speech":
    stimuli_pos = [30]
    stimuli_name = ['Speech.wav']
else:
    stimuli_pos = []
    stimuli_name = []
    quit()

# SDM = rir.Method("SDM", 20)
_0OA = rir.Method("0OA", 6)
_1OA = rir.Method("1OA", 6)
_2OA = rir.Method("2OA", 12)
_3OA = rir.Method("3OA", 20)
_4OA = rir.Method("4OA", 32)
# MP = rir.Method("MP", len(stimuli_pos))
methods = [_0OA,_1OA,_2OA,_3OA,_4OA]

root_dir = "C:\\Users\\Isaac\\Audio_files"
stimuli_dir = os.path.join(root_dir, "Stimuli\\Dry")

for method in methods:

    output_dir = os.path.join(root_dir, "Stimuli", method.name)

    for room in rooms:
        RIR_dir = os.path.join(root_dir, "Impulses", room.name, "Eigenmike", method.name)
        max_len = 0
        stimuli = []

        for i in range(len(stimuli_pos)):
            stimulus = os.path.join(stimuli_dir, stimuli_name[i])
            RIR = os.path.join(RIR_dir, room.name + "_" + method.name + "_" + str(stimuli_pos[i]) + "_Impulse.wav")
            stimuli.append([stimulus, RIR])
            temp_rir, fs = sf.read(RIR)
            if temp_rir.shape[0] > max_len:
                max_len = temp_rir.shape[0]

        temp_stim, fs = sf.read(stimuli[0][0])

        print("Convolving",method.name, room.name,"...")
        convolved = np.zeros([len(stimuli_pos), method.channels, len(temp_stim) + max_len - 1])

        for file_ind, files in enumerate(stimuli):
            dry, fs = sf.read(files[0])
            RIR, fs = sf.read(files[1])

            RIR = RIR.T

            if len(RIR.shape) > 1:
                for RIR_ind, LS in enumerate(RIR):
                    if len(LS) < max_len:
                        padding = np.zeros(max_len - len(LS))
                        LS = np.concatenate([LS, padding])
                    convolved[file_ind][RIR_ind] = signal.fftconvolve(dry / len(stimuli), LS)
            else:
                if len(RIR) < max_len:
                    padding = np.zeros(max_len - len(RIR))
                    RIR = np.concatenate([RIR, padding])
                convolved[file_ind][0] = signal.fftconvolve(dry / len(stimuli), RIR)

        if method.name is not "MP":
            output = np.sum(convolved, 0)
        else:
            output = np.sum(convolved, 1)

        for ind, channel in enumerate(output):
            if max(channel) >= 1:
                print("clipping")
            channel = (channel * (2 ** 15 - 1)).astype(np.int16)
            if mode is "TakeFive":
                filename = os.path.join(output_dir, room.name + "_" + method.name + "_TakeFive_" + str(ind) + ".wav")
            elif mode is "Dirac":
                filename = os.path.join(output_dir, room.name + "_" + method.name + "_Dirac_" + str(ind) + ".wav")
            elif mode is "Speech":
                filename = os.path.join(output_dir, room.name + "_" + method.name + "_Speech_" + str(ind) + ".wav")

            sf.write(filename, channel, fs)

