import os
import soundfile as sf
import numpy as np

root_dir = "C:\\Users\\craig\\Documents\\RIR_Project\\Audio_files"

stimuli_name = ['Piano.wav', 'Ride.wav', 'Kick.wav', 'Snare.wav', 'Sax.wav']
stimuli_dir = os.path.join(root_dir, "Stimuli\\Dry")

file = "delta (1).wav"

data = []
for ind, name in enumerate(stimuli_name):
    datum, fs = sf.read(os.path.join(stimuli_dir, name))
    data.append(datum)

data = np.array(data)
summed = np.sum(data, 0)
normalisation = np.amax(np.abs(summed))

print("stim max:", np.max(normalisation))

calibration_data, fs = sf.read(os.path.join(stimuli_dir, file))
delta_max = np.max(calibration_data)
print("delta pre:", delta_max)
calibration_data = calibration_data * normalisation / delta_max
print("delta post:", np.max(calibration_data))

sf.write(os.path.join(stimuli_dir, "test_norm.wav"), calibration_data/5, fs)