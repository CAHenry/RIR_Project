import PyRIR as rir
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

dodeca = [[1.5, 45, -35.2644],
          [1.5, 135, -35.2644],
          [1.5, 135, 35.2644],
          [1.5, -135, 35.2644],
          [1.5, -45, 35.2644],
          [1.5, -45, -35.2644],
          [1.5, -135, -35.2644],
          [1.5, 45, 35.2644],
          [1.5, 90, -69.0948],
          [1.5, -90, 69.0948],
          [1.5, -90, -69.0948],
          [1.5, 90, 69.0948],
          [1.5, 69.0948, 0],
          [1.5, 110.9052, 0],
          [1.5, -69.0948, 0],
          [1.5, -110.9052, 0],
          [1.5, 180, -20.9052],
          [1.5, 180, 20.9052],
          [1.5, 0, 20.9052],
          [1.5, 0, -20.9052]]

cube = [[1.5, 0, 0],
        [1.5, 90, 0],
        [1.5, 180, 0],
        [1.5, 270, 0],
        [1.5, 0, 90],
        [1.5, 0, -90]]

# HOA_cart = np.array([[0.574400008, 0.574400008, 0.574400008],
#                     [0.356799990, 0.000000000, 0.934199989],
#                     [-0.934199989, -0.356799990, 0.000000000],
#                     [0.934199989, 0.356799990, 0.000000000],
#                     [-0.574400029, 0.574400029, -0.574400029],
#                     [0.000000000, -0.934199989, -0.356799990],
#                     [-0.934199989, 0.356799990, 0.000000000],
#                     [0.574400008, -0.574400008, 0.574400008],
#                     [-0.574400008, 0.574400008, 0.574400008],
#                     [-0.574400008, -0.574400008, 0.574400008],
#                     [0.574400008, -0.574400008, -0.574400008],
#                     [0.356799990, 0.000000000, -0.934199989],
#                     [-0.574400008, -0.574400008, -0.574400008],
#                     [0.000000000, -0.934199989, 0.356799990],
#                     [0.000000000, 0.934199989, -0.356799990],
#                     [-0.356799990, 0.000000000, 0.934199989],
#                     [0.934199989, -0.356799990, 0.000000000],
#                     [-0.356799990, 0.000000000, -0.934199989],
#                     [0.574400008, 0.574400008, -0.574400008],
#                     [0.000000000, 0.934199989, 0.356799990]])
#
# HOA_cart = np.array([[0, 1, 0],
#                     [1, 0, 0],
#                     [0, -1, 0],
#                     [-1, 0, 0],
#                     [0, 0, 1],
#                     [0, 0, -1]])

# HOA_cart = [rir.spherical_2_cartesian(coord[0], coord[2], coord[1]) for coord in dodeca]
#
#
# HOA_sph = [rir.cartesian_2_spherical(coord[0], coord[1], coord[2]) for coord in HOA_cart]
#
# for ind, pos in enumerate(HOA_cart):
#     print(pos)
#     # print(pos[0], pos[1], pos[2])
#
# HOA_cart = np.array(HOA_cart).T
# fig = plt.figure(1)
# ax = Axes3D(fig)
# ax.scatter(HOA_cart[0], HOA_cart[1], HOA_cart[2])
#
# plt.show()

# cart = [rir.spherical_2_cartesian(cap) for cap in rir.eigenmike_capsules]
# print(cart)

for pos in dodeca:
    print(pos[1], pos[2], pos[0])