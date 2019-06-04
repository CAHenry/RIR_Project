import PyRIR as rir

print("<?xml version=\"1.0\"?>\n"
      "<BinauralApp>\n"
      "\t<ListenerPosX>0.000000000</ListenerPosX>\n"
      "\t<ListenerPosY>0.000000000</ListenerPosY>\n"
      "\t<ListenerPosZ>0.000000000</ListenerPosZ>\n"
      "\t<ListenerOrX>-0.000000000</ListenerOrX>\n"
      "\t<ListenerOrY>-0.000000000</ListenerOrY>\n"
      "\t<ListenerOrZ>0.000000000</ListenerOrZ>\n"
      "\t<ListenerOrW>1.000000000</ListenerOrW>\n"
      "\t<Platform>Windows</Platform>\n"
      "\t<OSCListenPort>12300</OSCListenPort>\n")

room = "Library"
root = "./.."
Direct = True
Mono_panned = True
Stereo = False    # TODO:remove
FOA2D = False    # TODO:remove
FOA = False
HOA = False
SDM = False

num_sources = Direct * 5 + Mono_panned * 5 + Stereo * 2 + FOA2D * 4 + FOA * 6 + HOA * 20 + SDM * 20
source = 0

print()


def print_source(num, pos, name, location, vol, vol_db, slider_pos=45):
    print("\t<Source%d_x>%.9f</Source%d_x>" % (num, pos[0], num))
    print("\t<Source%d_y>%.9f</Source%d_y>" % (num, pos[1], num))
    print("\t<Source%d_z>%.9f</Source%d_z>" % (num, pos[2], num))
    print("\t<Source%d_vol>%.9f</Source%d_vol>" % (num, vol, num))
    print("\t<Source%d_vol_dB>%.9f</Source%d_vol_dB>" % (num, vol_db, num))
    print("\t<Source%d_sliderPosition>%d</Source%d_sliderPosition>" % (num, slider_pos, num))
    file_path = location + "/" + name + ".wav"
    print("\t<Source_%d_filePath>%s</Source_%d_filePath>" % (num, file_path, num))


if Direct is True:
    positions = [30, 0, 0, 0, 330]
    names = ['Piano', 'Ride', 'Kick', 'Snare', 'Sax']
    location = root + "/Dry"
    distance = 1.3
    vol = 0.9
    vol_db = -40

    for ind, pos in enumerate(positions):
        cart = rir.spherical_2_cartesian(distance, 0, pos)
        print_source(source, cart, names[ind], location, vol, vol_db)
        source += 1
        print("\n")

if Mono_panned is True:
    positions = [30, 0, 0, 0, 330]
    names = ["%s_MP_%d" % (room, i) for i in range(len(positions))]
    location = root + "/MP"
    distance = 1.3
    vol = 0.1
    vol_db = -40

    for ind, pos in enumerate(positions):
        cart = rir.spherical_2_cartesian(distance, 0, pos)
        print_source(source, cart, names[ind], location, vol, vol_db)
        source += 1
        print("\n")

# if Stereo is True:
#     positions = [330, 30]
#     names = ["Stereo%s%d" % (room, i) for i in range(len(positions))]
#     location = root + "/Stereo"
#     distance = 1.3
#     vol = 0.1
#     vol_db = -40
#
#     for ind, pos in enumerate(positions):
#         cart = rir.spherical_2_cartesian(distance, 0, pos)
#         print_source(source, cart, names[ind], location, vol, vol_db)
#         source += 1
#         print("\n")
#
# if FOA2D is True:
#     positions = [[0,    90],
#                  [90,   90],
#                  [180,  90],
#                  [270,  90]]
#     names = ["1OA2D%s%d" % (room, i) for i in range(len(positions))]
#     location = root + "/1OA2D"
#     distance = 1
#     vol = 0.1
#     vol_db = -40
#
#     for ind, pos in enumerate(positions):
#         cart = rir.spherical_2_cartesian(distance, pos[1], pos[0])
#         print_source(source, cart, names[ind], location, vol, vol_db)
#         source += 1
#         print("\n")

if FOA is True:
    positions = [[0, 0],
                 [90, 0],
                 [180, 0],
                 [270, 0],
                 [0, 90],
                 [0, -90]]
    names = ["%s_1OA_%d" % (room, i) for i in range(len(positions))]
    location = root + "/1OA"
    distance = 1.5
    vol = 0.1
    vol_db = -40

    for ind, pos in enumerate(positions):
        cart = rir.spherical_2_cartesian(distance, pos[1], pos[0])
        print_source(source, cart, names[ind], location, vol, vol_db)
        source += 1
        print("\n")

if HOA is True:
    positions = [[-0.8660252935145808, 0.8660252935145805, -0.8660256243241122],
                 [-0.8660252935145806, -0.8660252935145808, -0.8660256243241122],
                 [-0.8660252935145806, -0.8660252935145808, 0.8660256243241122],
                 [0.8660252935145801, -0.8660252935145811, 0.8660256243241122],
                 [0.8660252935145805, 0.8660252935145808, 0.8660256243241122],
                 [0.8660252935145805, 0.8660252935145808, -0.8660256243241122],
                 [0.8660252935145801, -0.8660252935145811, -0.8660256243241122],
                 [-0.8660252935145808, 0.8660252935145805, 0.8660256243241122],
                 [-0.5352341753383809, -9.83209229433632e-17, -1.4012581409397211],
                 [0.5352341753383809, 1.6386820490560536e-16, 1.4012581409397211],
                 [0.5352341753383809, 1.6386820490560536e-16, -1.4012581409397211],
                 [-0.5352341753383809, -9.83209229433632e-17, 1.4012581409397211],
                 [-1.4012581409397213, 0.5352341753383802, 0.0],
                 [-1.4012581409397211, -0.5352341753383807, 0.0],
                 [1.4012581409397211, 0.535234175338381, 0.0],
                 [1.401258140939721, -0.5352341753383814, 0.0],
                 [1.7160462970810002e-16, -1.4012581409397211, -0.5352341753383812],
                 [1.7160462970810002e-16, -1.4012581409397211, 0.5352341753383812],
                 [-3.4320925941620003e-16, 1.4012581409397211, 0.5352341753383812],
                 [-3.4320925941620003e-16, 1.4012581409397211, -0.5352341753383812]]
    names = ["%s_3OA_%d" % (room, i) for i in range(len(positions))]
    location = root + "/3OA"
    distance = 1
    vol = 0.1
    vol_db = -40

    for ind, pos in enumerate(positions):
        print_source(source, pos, names[ind], location, vol, vol_db)
        source += 1
        print("\n")

if SDM is True:
    positions = [[0.577400008, 0.577400008, 0.577400008],
                 [0.356799990, 0.000000000, 0.934199989],
                 [-0.934199989, -0.356799990, 0.000000000],
                 [0.934199989, 0.356799990, 0.000000000],
                 [-0.577400029, 0.577400029, -0.577400029],
                 [0.000000000, -0.934199989, -0.356799990],
                 [-0.934199989, 0.356799990, 0.000000000],
                 [0.577400008, -0.577400008, 0.577400008],
                 [-0.577400008, 0.577400008, 0.577400008],
                 [-0.577400008, -0.577400008, 0.577400008],
                 [0.577400008, -0.577400008, -0.577400008],
                 [0.356799990, 0.000000000, -0.934199989],
                 [-0.577400008, -0.577400008, -0.577400008],
                 [0.000000000, -0.934199989, 0.356799990],
                 [0.000000000, 0.934199989, -0.356799990],
                 [-0.356799990, 0.000000000, 0.934199989],
                 [0.934199989, -0.356799990, 0.000000000],
                 [-0.356799990, 0.000000000, -0.934199989],
                 [0.577400008, 0.577400008, -0.577400008],
                 [0.000000000, 0.934199989, 0.356799990]]
    names = ["%s_SDM_%d" % (room, i) for i in range(len(positions))]
    location = root + "/SDM"
    distance = 1
    vol = 0.1
    vol_db = -40

    for ind, pos in enumerate(positions):
        print_source(source, pos, names[ind], location, vol, vol_db)
        source += 1
        print("\n")

print("</BinauralApp>")
