import os
import soundfile as sf
import numpy as np
from scipy import signal

num_channels = 20
order = '3OA'
output_dir = os.path.join("C:\\Users\\craig\\Documents\\RIR_Project\\Stimuli", order)
room = 'Library'

max_len = 0
stimuli_pos = [330, 0, 0, 0, 30]
stimuli_name = ['Piano.wav', 'Ride.wav', 'Kick.wav', 'Snare.wav', 'Sax.wav']
stimuli = []
stimuli_dir = "C:\\Users\\craig\\Documents\\RIR_Project\\Stimuli\\Dry"
RIR_dir = os.path.join("C:\\Users\\craig\\Documents\\RIR_Project\\RIRs", room, "Impulses\\Distance_cropped\\SDM\\SDM_decoded\\", order)

for i in range(len(stimuli_pos)):
    stimulus = os.path.join(stimuli_dir, stimuli_name[i])
    RIR = os.path.join(RIR_dir, room + "SDM" + str(stimuli_pos[i]) + "Ambi_dec.wav")
    stimuli.append([stimulus, RIR])
    temp_rir, fs = sf.read(RIR)
    if temp_rir.shape[0] > max_len:
        max_len = temp_rir.shape[0]


temp_stim, fs = sf.read(stimuli[0][0])

convolved = np.zeros([5, num_channels, len(temp_stim) + max_len - 1])


for file_ind, files in enumerate(stimuli):
    dry, fs = sf.read(files[0])
    RIR, fs = sf.read(files[1])
    print(RIR.shape)
    for RIR_ind, LS in enumerate(RIR.T):
        if RIR_ind == num_channels:
            break
        if len(LS) < max_len:
            padding = np.zeros(max_len-len(LS))
            LS = np.concatenate([LS, padding])
        convolved[file_ind][RIR_ind] = signal.fftconvolve(dry, LS)


output = np.sum(convolved, 0)
max_output = np.max(output)
for ind, channel in enumerate(output):
    channel = ((channel * (2**15 - 1)) / max_output).astype(np.int16)
    sf.write(os.path.join(output_dir, str(order)+ room + str(ind) + ".wav"), channel, fs)
