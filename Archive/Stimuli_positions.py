import tools


stim = [[1.3, 90, 330],
        [1.3, 90, 350],
        [1.3, 90, 0],
        [1.3, 90, 10],
        [1.3, 90, 30]]

# FOA = [[1, 90,  0],
#        [1, 90,  90],
#        [1, 90,  180],
#        [1, 90,  270],
#        [1, 0,   0],
#        [1, 180, 0]]

foa_cart = [tools.spherical_2_cartesian(coord[0], coord[1], coord[2]) for coord in stim]

for ind, pos in enumerate(foa_cart):
    print(pos)


