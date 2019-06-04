import numpy as np
import math


# converts spherical coordinates to cartesian coordinates, # phi is angle from the lateral plane,
# theta is azimuth and anti-clockwise
def spherical_2_cartesian(r, phi, theta):

    theta = np.deg2rad(360 - theta)
    phi = np.deg2rad(phi)

    x = r * np.cos(phi) * np.sin(theta)
    y = r * np.cos(phi) * np.cos(theta)
    z = r * np.sin(phi)

    return x, y, z

# Phi is angle from the lateral plane, theta is azimuth and anti-clockwise
def cartesian_2_spherical(x, y, z):

    r = np.sqrt(x**2 + y**2 + z**2)
    phi = np.arctan2(np.sqrt(x**2 + y**2), z)
    phi = np.arcsin(z/r)
    theta = np.arctan2(y, x)

    phi = np.mod(np.rad2deg(phi), 360)
    theta = np.mod(360 - np.rad2deg(theta), 360)

    return r, phi, theta


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
