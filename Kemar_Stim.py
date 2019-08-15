import PyRIR as rir
import os
import soundfile as sf
import numpy as np
from scipy import signal


# ----------------------------------------------------------------------------------------------------------------------
# Define directory, rooms and techniques
# ----------------------------------------------------------------------------------------------------------------------

lab = rir.Room("Audiolab", 0.3, 1.2, 1.3)
rooms = [lab]

root_dir = "C:\\Users\\craig\\Box Sync\\Papers\\Reverb study\\Audio_files"
stimuli_dir = os.path.join(root_dir, "Stimuli", "Dry")

apply_filter = False
# Filter: low shelf, g=-15db, fc=1khz from https://arachnoid.com/BiQuadDesigner/
sos = [0.91451797, -1.70941432, 0.80225341, 1, -1.69240694, 0.73377875]

modes = ["TakeFive", "Speech"]

for mode in modes:

    max_len_file = 0 # maximum file length after convolving, for zero padding

    print("Creating", mode, "stimuli...")

    if mode is "TakeFive":
        stimuli_pos = ["0"]
        stimuli_name = ['TakeFive_Piano.wav']
    elif mode is "Speech":
        stimuli_pos = ["0"]
        stimuli_name = ['Speech.wav']
    else:
        stimuli_pos = []
        stimuli_name = []
        quit()

    earcanal = rir.Method("Earcanal", 2)
    no_earcanal = rir.Method("No_Earcanal", 2)
    methods = [earcanal, no_earcanal]

    stimuli_dir = output_dir = os.path.join(root_dir, "Stimuli_07_08")
    if not os.path.isdir(stimuli_dir):
        print("Creating directory", stimuli_dir, "...")
        os.mkdir(stimuli_dir)

    for method in methods:

        output_dir = os.path.join(root_dir, "Stimuli_07_08", method.name)
        if not os.path.isdir(output_dir):
            print("Creating directory", output_dir, "...")
            os.mkdir(output_dir)

        for room in rooms:
            RIR_dir = os.path.join(root_dir, "Impulses_07_08", room.name, "Kemar", method.name)
            if not os.path.isdir(RIR_dir):
                print("Creating directory", RIR_dir, "...")
                os.mkdir(RIR_dir)

            max_len_RIR = 0
            stimuli = []

            # stimuli is a Nx2 matrix where each row has the dry audio at index 0 and the corresponding RIR at index 1
            for i in range(len(stimuli_pos)):
                stimulus = os.path.join(stimuli_dir, 'Dry', stimuli_name[i])
                RIR = os.path.join(RIR_dir, room.name + "_" + method.name + "_" + str(stimuli_pos[i]) + "_Impulse.wav")
                stimuli.append([stimulus, RIR])
                temp_rir, fs = sf.read(RIR)
                if temp_rir.shape[0] > max_len_RIR:
                    max_len_RIR = temp_rir.shape[0]

            temp_stim, fs = sf.read(stimuli[0][0])

            print("Convolving", method.name, room.name, "...")
            convolved = np.zeros([len(stimuli_pos), method.channels, len(temp_stim) + max_len_RIR - 1])

            for file_ind, files in enumerate(stimuli):
                dry, fs = sf.read(files[0])
                RIR, fs = sf.read(files[1])

                RIR = RIR.T

                for RIR_ind, LS in enumerate(RIR):
                    if len(LS) < max_len_RIR:
                        padding = np.zeros(max_len_RIR - len(LS))
                        LS = np.concatenate([LS, padding])
                    convolved[file_ind][RIR_ind] = signal.fftconvolve(dry / len(stimuli), LS)

            output = np.sum(convolved, 0) # Sum the first dimension (each stimulus) such that there is one file per LS
            if output.shape[1] > max_len_file:
                max_len_file = output.shape[1]

            for ind, channel in enumerate(output):


                if max(channel) >= 1:
                    print("clipping")

                if mode is "TakeFive":
                    filename = os.path.join(output_dir, room.name + "_" + method.name + "_TakeFive_" + str(ind) + ".wav")
                elif mode is "Dirac":
                    filename = os.path.join(output_dir, room.name + "_" + method.name + "_Dirac_" + str(ind) + ".wav")
                elif mode is "Speech":
                    filename = os.path.join(output_dir, room.name + "_" + method.name + "_Speech_" + str(ind) + ".wav")
                elif mode is "Dirac1":
                    filename = os.path.join(output_dir, room.name + "_" + method.name + "_Dirac1_" + str(ind) + ".wav")
                else:
                    filename = os.path.join(output_dir, room.name + "_" + method.name + "_Undefined_" + str(ind) + ".wav")

                sf.write(filename, channel, fs, subtype='PCM_24', format='WAV')

    # Zero-pad all the stimuli so all have the same length as the longest one
    print("Maximum length is", max_len_file)
    print("Zero-padding...")

    all_stimuli_dir = os.path.join(root_dir, "Stimuli_07_08")

    counter = 0
    for folder, subs, files in os.walk(all_stimuli_dir):
        for filename in files:
            if ".wav" in filename and mode in filename and "RVL" not in filename: # NOTE: the RVL bit is for when we are doing normal Ambi
                counter = counter + 1
                full_path = os.path.join(folder, filename)
                # print("Zero-padding", full_path,"...")
                data, fs = sf.read(full_path)
                datalen = data.shape[0]
                padded_data = np.zeros([max_len_file])
                padded_data[0:datalen] = data
                sf.write(full_path, padded_data, fs, subtype='PCM_24', format='WAV')


    print("Finished zero-padding", counter, mode, "files.")

print("Finished!")
