import numpy as np
import math


class Room:

    def __init__(self, name, rt_sixty, mic_height, mic_distance, DRR = None):
        self.name = name
        self.rt_sixty = rt_sixty
        self.mic_height = mic_height
        self.mic_distance = mic_distance
        self.DRR = DRR


class Measurement:

    def __init__(self, name, directions, capsules):
        self.name = name
        self.directions = directions
        self.n = len(directions)
        self.capsules = capsules


class Method:

    def __init__(self, name, channels):
        self.name = name
        self.channels = channels


# Phi is the angle from the lateral plane, theta is the azimuth and anti-clockwise
def spherical_2_cartesian(r, phi, theta):
    theta = np.deg2rad(theta)
    phi = np.deg2rad(phi)

    x = r * np.cos(phi) * np.cos(theta)
    y = r * np.cos(phi) * np.sin(theta)
    z = r * np.sin(phi)

    return [x, y, z]


# Phi is angle from the lateral plane, theta is azimuth and anti-clockwise
def cartesian_2_spherical(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    phi = np.arctan2(np.sqrt(x**2 + y**2), z)
    phi = np.arcsin(z/r)
    theta = np.arctan2(y, x)

    phi = np.mod(np.rad2deg(phi), 360)
    theta = np.mod(360 - np.rad2deg(theta), 360)

    return [r, phi, theta]


# Finds the angle between two points defined by cartesian coordinates. Angle aOb (O = origin)
def arc_angle_cartesian(a, b):
    return np.degrees(np.arccos((a[0] * b[0] + a[1] * b[1] + a[2] * b[2]) / np.sqrt(
        (a[0] ** 2 + a[1] ** 2 + a[2] ** 2) * (b[0] ** 2 + b[1] ** 2 + b[2] ** 2))))


# Finds the distance between two points defined by cartesian coordinates. Line ab
def distance_cartesian(a, b):
    return np.sqrt((b[0]-a[0])**2 + (b[1]-a[1])**2 + (b[2]-a[2])**2)


def perpendicular_vector(v):
    if math.isclose(v[0] + 1, 1) and math.isclose(v[1] + 1, 1):
        if math.isclose(v[2] + 1, 1):
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


# Finds the path difference of each capsule relative to the point on the eigenmike closest to the sound source.
def capsule_path_difference(points, point_source):
    paths = []
    radius = 0.042

    # convert point source, capsule potions and the closest point on 'sphere' of the microphone array to cartesian coord
    r = spherical_2_cartesian(radius, point_source[1], point_source[2])
    cart_source = spherical_2_cartesian(point_source[0], point_source[1], point_source[2])
    points = [spherical_2_cartesian(point[0], point[1], point[2]) for point in points]

    # find the distance to the edge of the sphere for capsules on the dark side
    edge = find_edge(r)
    prediffraction_path = distance_cartesian(cart_source, edge)

    r_path_length = distance_cartesian(cart_source, r)
    for p in points:
        # for each point find if it is on the dark or bright side of the array.
        angle = abs(arc_angle_cartesian(r, p))
        if angle <= 90:
            # if it is on the bright side find the distance between the capsule and the point source
            path_length = distance_cartesian(cart_source, p)
            paths.append(path_length - r_path_length)
        else:
            # if it is on the dark side find the path length on the curve and add it to the edge distance
            path_length = prediffraction_path + radius * np.sin(np.radians(angle - 90))
            paths.append(path_length - r_path_length)
    return paths


eigenmike_capsules = [[0.042, 21, 0],
                      [0.042, 0, 32],
                      [0.042, -21, 0],
                      [0.042, 0, 328],
                      [0.042, 58, 0],
                      [0.042, 35, 45],
                      [0.042, 0, 69],
                      [0.042, -35, 45],
                      [0.042, -58, 0],
                      [0.042, -35, 315],
                      [0.042, 0, 291],
                      [0.042, 35, 315],
                      [0.042, 69, 91],
                      [0.042, 32, 90],
                      [0.042, -31, 90],
                      [0.042, -69, 89],
                      [0.042, 21, 180],
                      [0.042, 0, 212],
                      [0.042, -21, 180],
                      [0.042, 0, 148],
                      [0.042, 58, 180],
                      [0.042, 35, 225],
                      [0.042, 0, 249],
                      [0.042, -35, 225],
                      [0.042, -58, 180],
                      [0.042, -35, 135],
                      [0.042, 0, 111],
                      [0.042, 35, 135],
                      [0.042, 69, 269],
                      [0.042, 32, 270],
                      [0.042, -32, 270],
                      [0.042, -69, 271]]

kemar_capsules = [[0.08, 0, 90],
                  [0.08, 0, 270]]

# values below set on June 4, from the normalizeLoudness.m script, using
# Reverb Only stimuli which were equalized with a lo-shelf filter (g=-15db,
# fc=1khz)
DRR_adjustment_trapezoid = [[0.82204, -1.7021],
                            [0.24951, -12.038],
                            [0.22887, -12.787],
                            [0.58886, -4.5997]]

DRR_adjustment_library = [[0.48533, -6.2793],
                          [0.17254, -15.241],
                          [0.14857, -16.54],
                          [0.35386, -9.0234]]
