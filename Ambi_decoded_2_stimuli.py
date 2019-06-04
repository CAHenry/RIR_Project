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

FOA = rir.Reproduction("1OA", 6)
HOA = rir.Reproduction("3OA", 20)
ambisonics = [FOA, HOA]

root_dir = "C:\\Users\\craig\\Documents\\RIR_Project\\Audio_files"

mode = "Dirac"

if mode is "Stimuli":
    stimuli_pos = [30, 0, 0, 0, 330]
    stimuli_name = ['Piano.wav', 'Ride.wav', 'Kick.wav', 'Snare.wav', 'Sax.wav']
elif mode is "Noise":
    stimuli_pos = [0]
    stimuli_name = ['PinkNoise.wav']
elif mode is "Dirac":
    stimuli_pos = [0]
    stimuli_name = ['Dirac.wav']
else:
    quit()

stimuli_dir = os.path.join(root_dir, "Stimuli\\Dry")

for room in rooms:
    RIR_dir = os.path.join(root_dir, "Impulses", room.name,
                           "Eigenmike\\ambisonic_decoded")
    for order in ambisonics:

        output_dir = os.path.join(root_dir, "Stimuli", order.name)
        max_len = 0
        stimuli = []
        for i in range(len(stimuli_pos)):
            stimulus = os.path.join(stimuli_dir, stimuli_name[i])
            RIR = os.path.join(RIR_dir, room.name + "_" + "Eigenmike" + "_" + str(stimuli_pos[i]) + "_" + "Ambi" + order.name + "_decoded.wav")
            stimuli.append([stimulus, RIR])
            temp_rir, fs = sf.read(RIR)
            if temp_rir.shape[0] > max_len:
                max_len = temp_rir.shape[0]

        temp_stim, fs = sf.read(stimuli[0][0])

        convolved = np.zeros([len(stimuli_pos), order.channels, len(temp_stim) + max_len - 1])

        for file_ind, files in enumerate(stimuli):
            dry, fs = sf.read(files[0])
            RIR, fs = sf.read(files[1])
            for RIR_ind, LS in enumerate(RIR.T):
                if len(LS) < max_len:
                    padding = np.zeros(max_len - len(LS))
                    LS = np.concatenate([LS, padding])
                convolved[file_ind][RIR_ind] = signal.fftconvolve(dry / len(stimuli), LS)

        output = np.sum(convolved, 0)

        for ind, channel in enumerate(output):
            channel = (channel * (2 ** 15 - 1)).astype(np.int16)

            if mode is "Stimuli":
                filename = os.path.join(output_dir, room.name + "_" + order.name + "_" + str(ind) + ".wav")
            elif mode is "Noise":
                filename = os.path.join(output_dir, room.name + "_" + order.name + "_Noise_" + str(ind) + ".wav")
            elif mode is "Dirac":
                filename = os.path.join(output_dir, room.name + "_" + order.name + "_Dirac_" + str(ind) + ".wav")

            sf.write(filename, channel, fs)

