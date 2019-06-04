import sounddevice as sd
import os
import scipy.io.wavfile

# Define room name, technique being recorded, the angle or position of the LS and the root dir containing the sweep
room_name = "turret"
technique = "Kemar"
identifier = "test"
root = "C:\\Users\\craig\\Documents\\RIR_Project\\RIRs"

# Creates the filepaths and directories needed
directory = os.path.join(root, room_name, "Sweeps", technique)
if not os.path.isdir(directory):
    os.makedirs(directory)
file_name = room_name + technique + identifier + "sweep.wav"
file_path = os.path.join(directory, file_name)


def get_overwrite():
    ans = raw_input("This file already exists, overwrite? (y/n): ")
    if ans == "n":
        quit()
    elif ans != "y":
        get_overwrite()
    else:
        return


if os.path.isfile(file_path):
    get_overwrite()

# Open and read the sweep. Must be called Sweep.wav
fs, sweep = scipy.io.wavfile.read(os.path.join(root, "Sweep.wav"))

# Settings for the audio input/output
sd.default.samplerate = fs
if technique is 'Kemar':
    sd.default.device = 'MOTU Audio ASIO, ASIO'
    print(sd.query_devices())
    sd.default.channels = [2, 2]
elif technique is 'SDM':
    sd.default.device = 'ASIO TCAT Dice EVM Platform, ASIO'
    sd.default.channels = [32, 32]

# Play the sweep whilst recording 32 channels
print("playing sweep")
rec = sd.playrec(sweep, blocking=True)

# Write the recording to a wav file
print("writing")
scipy.io.wavfile.write(file_path, fs, rec)
