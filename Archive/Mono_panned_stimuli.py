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

Mono_panned = rir.Reproduction("MP", len(stimuli_pos))

root_dir = "C:\\Users\\craig\\Documents\\RIR_Project\\Audio_files"

stimuli_dir = os.path.join(root_dir, "Stimuli\\Dry")

output_dir = os.path.join(root_dir, "Stimuli", Mono_panned.name)

for room in rooms:
    RIR, fs = sf.read(os.path.join(root_dir, "Impulses", room.name, "Eigenmike\\Mono_Panned\\normalised", room.name +"_Eigenmike_0_Impulse.wav"))
    RIR = RIR[:, 0]
    rir_len = len(RIR)

    stimuli = []

    for i in range(len(stimuli_pos)):
        stimulus = os.path.join(stimuli_dir, stimuli_name[i])
        stimuli.append([stimulus])

    temp_stim, fs = sf.read(stimuli[0][0])

    convolved = np.zeros([Mono_panned.channels, len(temp_stim) + rir_len - 1])

    for file_ind, files in enumerate(stimuli):
        dry, fs = sf.read(files[0])
        convolved[file_ind] = signal.fftconvolve(dry / len(stimuli), RIR)

    for ind, channel in enumerate(convolved):
        channel = (channel * (2 ** 15 - 1)).astype(np.int16)
        if mode is "Stimuli":
            filename = os.path.join(output_dir, room.name + "_" + Mono_panned.name + "_" + str(ind) + ".wav")
        elif mode is "Noise":
            filename = os.path.join(output_dir, room.name + "_" + Mono_panned.name + "_Noise_" + str(ind) + ".wav")
        elif mode is "Dirac":
            filename = os.path.join(output_dir, room.name + "_" + Mono_panned.name + "_Dirac_" + str(ind) + ".wav")

        sf.write(filename, channel, fs)

