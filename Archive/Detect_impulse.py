import os
import sys
import math
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import re


# https://dsp.stackexchange.com/questions/17121/calculation-of-reverberation-time-rt60-from-the-impulse-response

polar = [[0.042, 69, 0], [0.042, 90, 32],
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


# converts spherical coordinates to cartesian coordinates. Assumes clockwise azimuth and elevation from the z axis
def spherical_2_cartesian(r, theta, phi):

    theta = np.deg2rad(360 - theta)
    phi = np.deg2rad(phi)

    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)

    return x, y, z


# Finds the angle between two points defined by cartesian coordinates. Angle aOb (O = origin)
def arc_angle_cartesian(a, b):
    return np.degrees(np.arccos((a[0] * b[0] + a[1] * b[1] + a[2] * b[2]) / np.sqrt(
        (a[0] ** 2 + a[1] ** 2 + a[2] ** 2) * (b[0] ** 2 + b[1] ** 2 + b[2] ** 2))))


# Finds the distance between two points defined by cartesian coordinates. Line ab
def distance_cartesian(a, b):
    return np.sqrt((b[0]-a[0])**2 + (b[1]-a[1])**2 + (b[2]-a[2])**2)


def perpendicular_vector(v):
    if not np.nonzero(v[0]) and not np.nonzero(v[1]):
        if not np.nonzero(v[2]):
            # v is Vector(0, 0, 0)
            raise ValueError('zero vector')

        # v is Vector(0, 0, v.z)
        return [0, 1, 0]

    return [-v[1], v[0], 0]


def rotate(point, theta, u):
    r = [[np.cos(theta) + u[0]**2 * (1-np.cos(theta)),
             u[0] * u[1] * (1-np.cos(theta)) - u[2] * np.sin(theta),
             u[0] * u[2] * (1 - np.cos(theta)) + u[1] * np.sin(theta)],
            [u[0] * u[1] * (1-np.cos(theta)) + u[2] * np.sin(theta),
             np.cos(theta) + u[1]**2 * (1-np.cos(theta)),
             u[1] * u[2] * (1 - np.cos(theta)) - u[0] * np.sin(theta)],
            [u[0] * u[2] * (1-np.cos(theta)) - u[1] * np.sin(theta),
             u[1] * u[2] * (1-np.cos(theta)) + u[0] * np.sin(theta),
             np.cos(theta) + u[2]**2 * (1-np.cos(theta))]]
    rotated = []

    for i in range(3):
        rotated.append(sum([r[j][i] * point[j] for j in range(3)]))

    return rotated


def find_edge(point):
    x, y, z = point
    scale_factor = np.sqrt(x**2 + y**2 + z**2)
    unit = [x/scale_factor, y/scale_factor, z/scale_factor]

    axis_rotation = perpendicular_vector(unit)

    if not math.isclose(np.sqrt(axis_rotation[0]**2 + axis_rotation[1]**2 + axis_rotation[2]**2), 1):
        print("error")

    return rotate(point, np.pi/2, axis_rotation)


# Finds the path difference of each capsule relative to the point in the array closest to the sound source.
def capsule_path_difference(points, point_source):
    paths = []
    radius = 0.042

    r = spherical_2_cartesian(radius, point_source[1], point_source[2])
    cart_source = spherical_2_cartesian(point_source[0], point_source[1], point_source[2])
    r_path_length = distance_cartesian(cart_source, r)
    points = [spherical_2_cartesian(point[0], point[1], point[2]) for point in points]

    edge = find_edge(r)
    prediffraction_path = distance_cartesian(cart_source, edge)

    for p in points:
        angle = abs(arc_angle_cartesian(r, p))

        if angle <= 90:
            path_length = distance_cartesian(cart_source, p)
            paths.append(path_length - r_path_length)
        else:
            path_length = prediffraction_path + radius * np.sin(np.radians(angle - 90))
            paths.append(path_length - r_path_length)

    return paths


def onset_path(onsets_distance, onsets, paths):
    differences = []
    for ind_a, onset_a in enumerate(onsets):
        for ind_b, onset_b in enumerate(onsets):
            if ind_a is ind_b:
                break
            else:
                distance_onset_dif = abs(onsets_distance[ind_a] - onsets_distance[ind_b])
                real_onset_dif = abs(onset_a - onset_b)
                path_dif = abs(paths[ind_a] - paths[ind_b])
                predicted_onset_dif = round((path_dif / c) * 44100)
                differences.append([distance_onset_dif, real_onset_dif, predicted_onset_dif])
    return differences


room_name = "Trapezoid"
technique = "SDM"
root = "C:\\Users\\craig\\Documents\\RIR_Project\\RIRs"

RT60 = 1.5
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
cropped_distance_dir = os.path.join(directory, "Distance_cropped_2", technique)
cropped_threshold_dir = os.path.join(directory, "Threshold_cropped_2", technique)
if not os.path.isdir(cropped_distance_dir):
    os.makedirs(cropped_distance_dir)
if not os.path.isdir(cropped_threshold_dir):
    os.makedirs(cropped_threshold_dir)

fc = 3000 / 22050
b, a = signal.butter(10, fc, 'low')

for file_name in os.listdir(files_dir):

    direction = re.findall("\d+", file_name)[0]

    paths = capsule_path_difference(polar, [1.5, 0, direction])
    max_channel, min_channel, max_onset, min_onset = 0, 0, 0, sys.maxsize

    onsets = []

    # Read wav file
    data,  fs = sf.read(os.path.join(files_dir, file_name))

    closest = np.argmin(paths)
    # low pass filter at fc
    filtered = signal.filtfilt(b, a, data.T[closest])
    filter_max = max(filtered)
    closest_onset = next(x[0] for x in enumerate(filtered) if abs(x[1]) == filter_max)
    time = [n / fs for n in range(filtered.size)]

    onsets_distance = np.array([round(((paths[i] - paths[closest]) / c) * fs) + closest_onset for i in range(len(paths))], dtype='int32')

    for ind, channel in enumerate(data.T):

        onset = onsets_distance[ind]
        # plt.figure(ind + 1)
        # plt.axvline(x=onset / fs, color='r')
        # time = [n / fs for n in range(channel.size)]
        # plt.plot(time[int(onset - (fs / 1000)): int(onset + (fs / 400))], data.T[ind][int(onset - (fs / 1000)):
        #                                                                               int(onset + (fs / 400))])
    # plt.show()

    # # low pass filter at fc
    filtered = []
    for ind, channel in enumerate(data.T):
        channel_max = max(channel)
        filtered.append(signal.filtfilt(b, a, channel))

    maximum = np.amax(filtered)

    for ind, channel in enumerate(filtered):
        channel_max = max(channel)
        scaled = np.array([n / channel_max * maximum for n in channel])
        onset = next(x[0] for x in enumerate(scaled) if abs(x[1]) == maximum)
        onsets.append(onset)

    cropped_distance, cropped_threshold = np.empty(data.T.shape, dtype='float64'), np.empty(data.T.shape, dtype='float64')
    dist_crop = int(np.amin(onsets_distance) - fade_length + crop_amount)
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
            cropped_threshold[ind][dist_crop+i] *= hamming_scale
            cropped_threshold[ind][thresh_crop+i] *= hamming_scale
        # plt.plot(ham)
        # plt.show()

    first_sample_dist = np.amin(onsets_distance) - predirect_samps
    first_sample_thresh = np.amin(onsets) - predirect_samps
    output_distance = np.delete(cropped_distance, np.s_[:first_sample_dist], axis=1)
    output_threshold = np.delete(cropped_threshold, np.s_[:first_sample_thresh], axis=1)

    last_sample_dist = int(np.amax(onsets_distance) - predirect_samps + round(RT60 * fs)) - first_sample_dist
    last_sample_thresh = int(np.amax(onsets) - predirect_samps + round(RT60 * fs)) - first_sample_thresh

    output_distance = np.delete(output_distance, np.s_[last_sample_dist:], axis=1).T
    output_threshold = np.delete(output_threshold, np.s_[last_sample_thresh:], axis=1).T

    for i in range(fade_length):
        n = fade_length - i
        hamming_scale = 0.54 + 0.46 * np.cos((2 * np.pi * n) / (2 * fade_length))
        output_distance[:][-i] *= hamming_scale
        output_threshold[:][-i] *= hamming_scale

    sf.write(os.path.join(cropped_distance_dir, file_name), output_distance, 44100)
    sf.write(os.path.join(cropped_threshold_dir, file_name), output_threshold, 44100)

        # if onset > max_onset:
        #     max_onset = onset
        #     max_channel = ind
        #
        # if onset < min_onset:
        #     min_onset = onset
        #     min_channel = ind
        # time = [n / fs for n in range(channel.size)]
        # plt.figure(ind + 1)
        # plt.axvline(x=onset/fs, color='b')
        # print(onset + (fs / 100))
        # plt.plot(time[int(onset - (fs / 1000)): int(onset + (fs / 400))], data.T[ind][int(onset - (fs / 1000)): int(onset + (fs / 400))])
    # plt.show()
    # print(((max_onset-min_onset) / fs) * c)
    # print(max_channel)
    # print(min_channel)

    # results = np.array(onset_path(onsets_distance, onsets, paths))
    # difference_distance = results.T[0] - results.T[2]
    # average_distance = np.mean(difference_distance)
    #
    # difference_threshold = results.T[0] - results.T[1]
    # average_threshold = np.mean(difference_threshold)
    # print(file_name)
    # print('%f' % average_distance)
    # print('%f' % average_threshold)
    # plt.figure(50)
    # plt.boxplot(weighted_error)
    # plt.scatter(results.T[0], results.T[1])
    # plt.show()
