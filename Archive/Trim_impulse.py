import numpy as np
import os
from scipy import signal
from scipy import stats
from scipy import integrate
import soundfile as sf
from tools import capsule_path_difference
import re
import matplotlib.pyplot as plt

# User input, room, technique, distance, height, capsule positions

capsules_polar = [[0.042, 69, 0], [0.042, 90, 32],
                  [0.042, 111, 0], [0.042, 90, 328],
                  [0.042, 32, 0], [0.042, 55, 45],
                  [0.042, 90, 69], [0.042, 125, 45],
                  [0.042, 148, 0], [0.042, 125, 315],
                  [0.042, 90, 291], [0.042, 55, 315],
                  [0.042, 21, 91], [0.042, 58, 90],
                  [0.042, 121, 90], [0.042, 159, 89],
                  [0.042, 69, 180], [0.042, 90, 212],
                  [0.042, 111, 180], [0.042, 90, 148],
                  [0.042, 32, 180], [0.042, 55, 225],
                  [0.042, 90, 249], [0.042, 125, 225],
                  [0.042, 148, 180], [0.042, 125, 135],
                  [0.042, 90, 111], [0.042, 55, 135],
                  [0.042, 21, 269], [0.042, 58, 270],
                  [0.042, 122, 270], [0.042, 159, 271]]

room_name = "Library"
technique = "SDM"
root = "C:\\Users\\craig\\Documents\\RIR_Project\\RIRs"

distance = 1.5
height = 1.2
c = 343.0
leeway = 20  # How many samples leeway are before the first order reflection to be completely certain
fade_length = 10  # The length of the fade up before the leeway in samples
predirect_secs = 0.00608  # The amount of time before the direct sound in the HRIR that this BRIR is to be synced to.

# calcs from user input
predirect = round(predirect_secs * 44100.0)
toa = distance / c
first = (np.sqrt(height**2 + (distance/2)**2) * 2) / c
dif = first-toa
crop_amount = round((first - toa) * 44100) - leeway
# Open files and directories correctly

directory = os.path.join(root, room_name, "Impulses")
files_dir = os.path.join(directory, technique)

cropped_distance_dir = os.path.join(directory, "Distance_cropped", technique)
cropped_threshold_dir = os.path.join(directory, "Threshold_cropped", technique)
if not os.path.isdir(cropped_distance_dir):
    os.makedirs(cropped_distance_dir)
if not os.path.isdir(cropped_threshold_dir):
    os.makedirs(cropped_threshold_dir)

# initialise the filters

fc = 400 / 22050
b_RT, a_RT = signal.butter(10, fc, 'low')

fc = 3000 / 22050
b_onset, a_onset = signal.butter(10, fc, 'low')

# loop through files

for file_name in os.listdir(files_dir):

    data,  fs = sf.read(os.path.join(files_dir, file_name))
    azimuth = [int(s) for s in re.findall(r'\d+', file_name)]

    # parse through the impulses and filter them
    filtered = []
    for ind, channel in enumerate(data.T):
        channel_max = max(channel)
        filtered.append(signal.filtfilt(b_onset, a_onset, channel))

    # parse through the impulses, find their onsets
    maximum = np.amax(filtered)
    onsets = []
    for ind, channel in enumerate(filtered):
        channel_max = max(channel)
        scaled = np.array([n / channel_max * maximum for n in channel])
        onset = next(x[0] for x in enumerate(scaled) if abs(x[1]) == maximum)
        onsets.append(onset)

    # calculate onsets due to path difference relative to the closest onset
    paths = capsule_path_difference(capsules_polar, [distance, 90, azimuth[0]])
    closest = np.argmin(paths)
    distance_onsets = np.array([round(((paths[i] - paths[closest]) / c) * fs) + onsets[closest] for i in range(len(paths))], dtype='int32')

    t60 = []
    # parse again, find RT60 of closest capsule. Find limits first
    for ind, channel in enumerate(data.T):
        analytic = signal.hilbert(channel)
        envelope = signal.filtfilt(b_RT, a_RT, analytic)
        N = 5001
        envelope = np.convolve(analytic, np.ones((N,)) / N, mode='valid')

        amplitude_envelope = np.abs(envelope)
        energy_envelope = 20 * np.log10(amplitude_envelope / max(amplitude_envelope))

        noise = np.median(energy_envelope[:])
        interval = 0.001
        window_size = 0.001
        upperlimit = -10
        i = 0
        maximum = channel[onsets[ind]]
        Ti = 0
        passed = False
        while True:
            start = round(onsets[ind] + i * interval * fs)
            end = round(onsets[ind] + (i * interval + window_size) * fs)
            segment = energy_envelope[start:end]
            sub_level = np.mean(segment)

            # if sub_level > maximum:
            #     maximum = sub_level

            if (sub_level < maximum + upperlimit) and (Ti is 0):
                Ti = onsets[ind] + round((i * interval + window_size / 2) * fs)

            if sub_level < noise:
                Td = onsets[ind] + round((i * interval + window_size / 2) * fs)
                break

            i += 1

        hA = energy_envelope[Ti:Td] ** 2
        # lt = [(np.cumsum(hA[Td - i * 1:Td]) / np.sum(hA[Ti:Td])) for i in range(Ti, Td)]

        lt = ((np.cumsum(hA[::-1]) / np.sum(hA[:]) * -30) + upperlimit)

        # lt = np.flip(np.array(lt, dtype=float))
        plt.plot([x for x in range(Ti, Td)], lt, color='g')
        plt.plot(energy_envelope[0:Td*2], color='y')
        plt.axvline(x=Ti, color='b')
        plt.axvline(x=Td, color='r')

        plt.show()

        # Schroeder integration
        # sch = np.cumsum(energy_envelope[Ti:Td]**2)
        # sch_db = 10.0 * np.log10(sch / np.max(sch))

        # # https://github.com/python-acoustics/python-acoustics/blob/master/acoustics/room.py
        # init = -5.0
        # end = -35.0
        # factor = 2
        #
        # # Schroeder integration
        # abs_signal = np.abs(channel) / np.max(np.abs(channel))
        # sch = np.cumsum(abs_signal[::-1] ** 2)[::-1]
        # sch_db = 10.0 * np.log10(sch / np.max(sch))
        #
        # # Linear regression
        # sch_init = sch_db[np.abs(sch_db - init).argmin()]
        # sch_end = sch_db[np.abs(sch_db - end).argmin()]
        # init_sample = np.where(sch_db == sch_init)[0][0]
        # end_sample = np.where(sch_db == sch_end)[0][0]
        # x = np.arange(init_sample, end_sample + 1) / fs
        # y = sch_db[init_sample:end_sample + 1]
        # slope, intercept = stats.linregress(x, y)[0:2]
        #
        # # Reverberation time (T30, T20, T10 or EDT)
        # db_regress_init = (init - intercept) / slope
        # db_regress_end = (end - intercept) / slope
        # t60.append(factor * (db_regress_end - db_regress_init))

        # print(t60[ind])
        #
        # line = [slope * x + intercept for x in range(len(sch_db))]

        # plt.plot(line, color='g')
        # plt.axvline(x=init_sample, color='b')
        # plt.axvline(x=init_sample + (t60 * fs), color='r')
        # plt.plot(energy_envelope, color='y')
        #
        # plt.show()

        # Replace direct sound with digital silence up to leeway

    cropped_distance, cropped_threshold = np.empty(data.T.shape, dtype='float64'), np.empty(data.T.shape,
                                                                                                dtype='float64')
    dist_crop = int(np.amin(distance_onsets) - fade_length + crop_amount)
    thresh_crop = int(np.amin(onsets) - fade_length + crop_amount)

    for ind, channel in enumerate(data.T):

        cropped_distance[ind] = channel
        cropped_threshold[ind] = channel

        # dist_crop = int(onsets_distance[ind] - fade_length + crop_amount)
        # thresh_crop = int(onsets[ind] - fade_length + crop_amount)
        cropped_distance[ind][:dist_crop] = 0
        cropped_threshold[ind][:thresh_crop] = 0

        ham = []
        for i in range(fade_length):
            n = fade_length - i
            hamming_scale = 0.54 + 0.46 * np.cos((2 * np.pi * n) / (2 * fade_length))
            ham.append(hamming_scale)
            cropped_threshold[ind][dist_crop + i] *= hamming_scale
            cropped_threshold[ind][thresh_crop + i] *= hamming_scale
        # plt.plot(ham)
        # plt.show()

    rt60 = np.median(t60)
    first_sample_dist = np.amin(distance_onsets) - predirect
    first_sample_thresh = np.amin(onsets) - predirect
    last_sample_dist = int(np.amax(distance_onsets) - predirect + round(rt60 * fs)) - first_sample_dist
    last_sample_thresh = int(np.amax(onsets) - predirect + round(rt60 * fs)) - first_sample_thresh
    output_distance = np.delete(cropped_distance, np.s_[:first_sample_dist], axis=1)
    output_threshold = np.delete(cropped_threshold, np.s_[:first_sample_thresh], axis=1)

    output_distance = np.delete(output_distance, np.s_[last_sample_dist:], axis=1).T
    output_threshold = np.delete(output_threshold, np.s_[last_sample_thresh:], axis=1).T

    sf.write(os.path.join(cropped_distance_dir, file_name), output_distance, 44100)
    sf.write(os.path.join(cropped_threshold_dir, file_name), output_threshold, 44100)
# Crop file according to predirect gap and the RT60 added to the furthest capsule, fade out for the end.