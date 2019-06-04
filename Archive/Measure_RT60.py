import os
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

# https://dsp.stackexchange.com/questions/17121/calculation-of-reverberation-time-rt60-from-the-impulse-response

room_name = "Library"
technique = "SDM"
root = "C:\\Users\\craig\\Documents\\RIR_Project\\RIRs"

distance = 1.5
height = 1.2
c = 343.0

safety = 20
fade_length = 10
predirect_secs = 0.00608
predirect_samps = round(predirect_secs * 44100.0)

toa = distance / c
first = (np.sqrt(height**2 + (distance/2)**2) * 2) / c
dif = first-toa
crop_amount = round((first - toa) * 44100) - safety

# Creates the filepaths and directories needed
directory = os.path.join(root, room_name, "Impulses")
files_dir = os.path.join(directory, technique)

fc = 400 / 22050
b, a = signal.butter(10, fc, 'low')

for file_name in os.listdir(files_dir):

    data,  fs = sf.read(os.path.join(files_dir, file_name))

    for channel in data.T:
        analytic = signal.hilbert(channel)
        envelope = signal.filtfilt(b, a, analytic)
        N = 5001
        envelope = np.convolve(analytic, np.ones((N,)) / N, mode='valid')
        # plt.plot(analytic.real)
        # plt.plot(analytic.imag)
        amplitude_envelope = np.abs(envelope)
        energy_envelope = 20 * np.log10(amplitude_envelope / max(amplitude_envelope))

        noise = np.median(energy_envelope[:])
        # avg = np.mean(energy_envelope[100000:500000])
        # plt.axhline(noise, color='b')
        # plt.axhline(avg, color='r')
        #
        # plt.plot(energy_envelope)
        # plt.show()
        interval = 0.01
        window_size = 0.01
        i = 0
        maximum = -100
        Ti = 0
        passed = False
        while True:
            start = round(i * interval * fs)
            end = round((i * interval + window_size) * fs)
            segment = energy_envelope[start:end]
            sub_level = np.mean(segment)

            if sub_level > maximum:
                maximum = sub_level

            if sub_level >= maximum:
                passed = True

            if (sub_level < maximum - 5) and passed and (Ti is not 0):
                Ti = i
                passed = False

            if sub_level < noise:
                break

            i += 1

        plt.axvline(x=round((Ti * interval + window_size / 2) * fs), color='b')
        plt.axvline(x=round((i * interval + window_size / 2) * fs), color='r')
        plt.plot(energy_envelope)
        plt.show()

    break
# http://research.spa.aalto.fi/publications/theses/vesa_mst/vesa_mst_pres.pdf
# http://lib.tkk.fi/Dipl/2004/urn007943.pdf
# file:///C:/Users/craig/Downloads/BS%20EN%20ISO%20354-2003--[2019-04-16--01-31-30%20PM].pdf
# Find the limits of the integration

# Td = 5 dB down from the maximum points
# Ti = When the signal reaches the noise floor. ISO 3382 standard specifies that Ti should be set to a point where
# the impulse response is 5 dB above the noise floor. Find median dB, from onset find average of 0.05s windows. When it
# is lower than 5dB above the median - Ti

# Backwards integrate (Schroeder)

# LS fit (T20 or T30??)
