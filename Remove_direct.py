# ----------------------------------------------------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------------------------------------------------

import PyRIR as rir
import os
import soundfile as sf
from scipy import signal
import numpy as np
import re
import scipy.io.wavfile

# ----------------------------------------------------------------------------------------------------------------------
# Define directory, rooms and techniques
# ----------------------------------------------------------------------------------------------------------------------

library = rir.Room("Library", 1.5, 1.2, 1.5)    # name, rt60, mic_height, mic_distance
trapezoid = rir.Room("Trapezoid", 0.9, 1.2, 1.2)
rooms = [library, trapezoid]

rvl_brir = rir.Measurement("RVL", ["0", "90", "180", "270", "top", "bottom"], rir.kemar_capsules)
methods = [rvl_brir]

root_dir = "C:\\Users\\craig\\Box Sync\\Papers\\Reverb study\\Audio_files"

# ----------------------------------------------------------------------------------------------------------------------
# Trim each sweep, Direct sound to end of RT60(user input). Direct sound is then replaced with zero padding
# ----------------------------------------------------------------------------------------------------------------------
fs = 44100
c = 343
safety = 1    # Safety net x many samples long placed between the fade at the calculated first reflection
fade_length = 30    # Length of the cosine fade in samples

# Impulse detection LPF initialisation
fc = 3000 / (fs / 2)
b, a = signal.butter(10, fc, 'low')

# Create half hamming window for fade in and out
ham = []
for i in range(fade_length):
    n = fade_length - i
    hamming_scale = 0.54 + 0.46 * np.cos((2 * np.pi * n) / (2 * fade_length))
    ham.append(hamming_scale)

for room in rooms:
    # Calculate the difference in time of arrival for the direct and the floor reflection
    direct = room.mic_distance / c
    floor_reflection = (np.sqrt(room.mic_height ** 2 + (room.mic_distance / 2) ** 2) * 2) / c
    toa_difference = floor_reflection - direct

    for method in methods:
        # create directory
        raw_dir = os.path.join(root_dir, "Impulses_07_08", room.name, method.name, "BRIR")
        if not os.path.isdir(raw_dir):
            os.makedirs(raw_dir)
        trimmed_dir = os.path.join(root_dir, "Impulses_07_08", room.name, method.name, "BRIR_no_direct")
        if not os.path.isdir(trimmed_dir):
            os.makedirs(trimmed_dir)

        for file_name in os.listdir(raw_dir):
            paths = []

            if "top" in file_name:
                paths = rir.capsule_path_difference(method.capsules, [room.mic_distance, 90, 0])
            elif "bottom" in file_name:
                paths = rir.capsule_path_difference(method.capsules, [room.mic_distance, -90, 0])
            else:
                direction = int(re.findall("\d+", file_name)[0])
                paths = rir.capsule_path_difference(method.capsules, [room.mic_distance, 0, direction])

            # Read wav file
            data, fs = sf.read(os.path.join(raw_dir, file_name))
            # low pass filter the signal at the closest capsule at fc
            closest_capsule = np.argmin(paths)

            audio = data.T
            audio = np.delete(audio, np.s_[:int(0.2*fs)], axis=1)


            # Calculate the onset of the remaining capsules based on the TOA difference between the closest capsule and the capsule in question
            onsets = np.array([round(((paths[i] - paths[closest_capsule]) / c) * fs) for i in range(len(paths))], dtype='int32')

            # initialise empty output array
            output = np.empty(audio.shape, dtype='float64')

            for ind, channel in enumerate(audio):
                output[ind] = channel

                # the data is set to zero up to the first reflection with a bit of leeway and leaving space for the fade
                zeroed_amount = int(onsets[ind] + round(toa_difference * 44100) - safety - fade_length)
                output[ind][:zeroed_amount] = 0

                zeroed_amount = 0

                # fade in
                for i in range(fade_length):
                    output[ind][zeroed_amount + i] *= ham[i]

            # crop based on the RT60 of the room
            last_sample = int(np.amax(onsets) + round(room.rt_sixty * fs))
            output = np.delete(output, np.s_[last_sample:], axis=1).T

            # fade out
            for i in range(fade_length):
                output[:][-i] *= ham[i]

            print(os.path.join(trimmed_dir, file_name))

            sf.write(os.path.join(trimmed_dir, file_name), output, fs, subtype='PCM_24', format='WAV')
