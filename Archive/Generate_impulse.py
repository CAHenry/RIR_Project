import os
import struct
import wave
from scipy import signal
import numpy as np
import scipy.io.wavfile
import soundfile as sf

# def read_wav(file_path, output_dtype='int32'):
#     """ return list with interleaved samples """
#     wav_file = wave.open(file_path, 'rb')
#     channels = wav_file.getnchannels()
#     n_frames = wav_file.getnframes()
#     sample_width = wav_file.getsampwidth()
#     if sample_width == 3: #have to read this one sample at a time
#         s = ''
#         for frame in xrange(n_frames):
#             fr = wav_file.readframes(1)
#             for c in xrange(0,3*channels,3):
#                 s += '\0'+fr[c:(c+3)] # put TRAILING 0 to make 32-bit (file is little-endian)
#     else:
#         s = wav_file.readframes(n_frames)
#     wav_file.close()
#     unpstr = '<{0}{1}'.format(n_frames*channels, {1:'b',2:'h',3:'i',4:'i',8:'q'}[sample_width])
#     byte_like = list(struct.unpack(unpstr, s))
#
#     data = np.zeros((n_frames, channels), dtype=output_dtype)
#     if sample_width == 3:
#         if output_dtype == 'float32':
#             for i, sample in enumerate(byte_like):
#                 data[i / channels][i % channels] = float(sample >> 8) / np.exp2((sample_width * 8) - 1)
#         else:
#             for i, sample in enumerate(byte_like):
#                 data[i/channels][i % channels] = sample >> 8
#     elif output_dtype == 'float32':
#         for i, sample in enumerate(byte_like):
#             data[i/channels][i % channels] = float(sample) / np.exp2((sample_width * 8) - 1)
#     else:
#         for i, sample in enumerate(byte_like):
#             data[i/channels][i % channels] = sample
#
#     return data, channels, n_frames


# Define room name, technique being recorded, the angle or position of the LS and the root dir containing the sweep
room_name = "Library"
technique = "Kemar"
root = "C:\\Users\\craig\\Documents\\RIR_Project\\RIRs"
directory = os.path.join(root, room_name)
sweep_dir = os.path.join(directory, "Sweeps", technique)
impulse_dir = os.path.join(directory, "Impulses", technique, "test")
if not os.path.isdir(impulse_dir):
    os.makedirs(impulse_dir)

inverse, fs = sf.read(os.path.join(root, "Inverse.wav"))

clipping = 0

for file_name in os.listdir(sweep_dir):
    sweep_recording, fs = sf.read(os.path.join(sweep_dir, file_name))
    impulses = []
    for i, sweep in enumerate(sweep_recording.T):

        impulse = signal.fftconvolve(sweep, inverse)
        impulses.append(impulse)
        maximum = impulse.max()
        if maximum > clipping:
            clipping = maximum

    impulses = np.float32(np.array(impulses).T)

    impulse_file_name = file_name.replace("sweep", "impulse")
    scipy.io.wavfile.write(os.path.join(impulse_dir, impulse_file_name), 44100, impulses)
print("normalising")
for file_name in os.listdir(impulse_dir):
    fs, impulses = scipy.io.wavfile.read(os.path.join(impulse_dir, file_name))
    impulses = np.array(impulses / clipping)

    start_seconds = 10
    # end_seconds = 12
    trimmed_impulses = impulses[start_seconds * fs:, :]

    scipy.io.wavfile.write(os.path.join(impulse_dir, file_name), 44100, trimmed_impulses)
