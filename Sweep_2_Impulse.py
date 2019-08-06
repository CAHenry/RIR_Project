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

kemar = rir.Measurement("Kemar", ["0", "90", "180", "270", "top", "bottom"], rir.kemar_capsules)
eigenmike = rir.Measurement("Eigenmike", [str(x) for x in range(0, 360, 10)], rir.eigenmike_capsules)
methods = [kemar, eigenmike]

root_dir = "C:\\Users\\craig\\Documents\\RIR_Project\\Audio_files"

# ----------------------------------------------------------------------------------------------------------------------
# Convolve every measured sweep with the inverse and trim the first ten seconds (silence)
# ----------------------------------------------------------------------------------------------------------------------

# Inverse sweep - Farina's method
inverse, fs = sf.read(os.path.join(root_dir, "Inverse.wav"))

for room in rooms:

    for method in methods:
        # Create file directories
        sweep_dir = os.path.join(root_dir, "Sweeps", room.name, method.name)
        if not os.path.isdir(sweep_dir):
            os.makedirs(sweep_dir)

        impulse_dir = os.path.join(root_dir, "Impulses", room.name, method.name, "raw")
        if not os.path.isdir(impulse_dir):
            os.makedirs(impulse_dir)


        # the highest value across all measurements within the room/method combo
        measurement_max = 0

        for file_name in os.listdir(sweep_dir):

            sweeps, fs = sf.read(os.path.join(sweep_dir, file_name))
            impulses = []

            # Convolve each channel by the inverse and check if it has the highest amplitude so far
            for i, sweep in enumerate(sweeps.T):
                impulse = signal.fftconvolve(sweep, inverse)
                impulses.append(impulse)
                file_max = impulse.max()
                if file_max > measurement_max:
                    measurement_max = file_max

            impulses = np.array(impulses).T
            impulse_file_name = file_name.replace("Sweep", "Impulse")
            # write each file using scipy because it doesn't clip the data - sf.write breaks this!
            print(os.path.join(impulse_dir, impulse_file_name))
            scipy.io.wavfile.write(os.path.join(impulse_dir, impulse_file_name), 44100, impulses)

        # Normalise each file, delete the first ten seconds and rewrite
        for file_name in os.listdir(impulse_dir):
            impulses, fs = sf.read(os.path.join(impulse_dir, file_name))
            impulses = np.array(impulses / measurement_max)
            impulses = impulses[10 * fs:, :]
            print(os.path.join(impulse_dir, file_name))
            # sf.write(os.path.join(impulse_dir, file_name), impulses, fs)
            scipy.io.wavfile.write(os.path.join(impulse_dir, file_name), fs, impulses)


# ----------------------------------------------------------------------------------------------------------------------
# Trim each sweep, Direct sound to end of RT60(user input). Direct sound is then replaced with zero padding
# ----------------------------------------------------------------------------------------------------------------------
fs = 44100
c = 343
safety = 30    # Safety net x many samples long placed between the fade at the calculated first reflection
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
        raw_dir = os.path.join(root_dir, "Impulses", room.name, method.name, "raw")
        if not os.path.isdir(raw_dir):
            os.makedirs(raw_dir)
        trimmed_dir = os.path.join(root_dir, "Impulses", room.name, method.name, "trimmed")
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
            filtered = signal.filtfilt(b, a, data.T[closest_capsule])
            # find the sample containing the maximum amplitude of the filtered signal
            filter_max = max(filtered)
            closest_onset = next(x[0] for x in enumerate(filtered) if abs(x[1]) == filter_max)

            # Calculate the onset of the remaining capsules based on the TOA difference between the closest capsule and the capsule in question
            onsets = np.array([round(((paths[i] - paths[closest_capsule]) / c) * fs) + closest_onset for i in range(len(paths))], dtype='int32')

            # initialise empty output array
            cropped_data = np.empty(data.T.shape, dtype='float64')

            for ind, channel in enumerate(data.T):
                cropped_data[ind] = channel
                # the data is set to zero up to the first reflection with a bit of leeway and leaving space for the fade
                zeroed_amount = int(onsets[ind] + round(toa_difference * 44100) - safety - fade_length)
                cropped_data[ind][:zeroed_amount] = 0

                # fade in
                for i in range(fade_length):
                    cropped_data[ind][zeroed_amount + i] *= ham[i]

            # crop based on the first onset and the zero padding of the HRTF.
            first_sample = np.amin(onsets)
            output = np.delete(cropped_data, np.s_[:first_sample], axis=1)
            # crop based on the RT60 of the room
            last_sample = int(np.amax(onsets) + round(room.rt_sixty * fs)) - first_sample
            output = np.delete(output, np.s_[last_sample:], axis=1).T

            # fade out
            for i in range(fade_length):
                output[:][-i] *= ham[i]

            print(os.path.join(trimmed_dir, file_name))

            # sf.write(os.path.join(trimmed_dir, file_name), output, fs)
            scipy.io.wavfile.write(os.path.join(trimmed_dir, file_name), fs, output)
