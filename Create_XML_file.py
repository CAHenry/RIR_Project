import os
import PyRIR as rir
import numpy as np

xml_name_base = "Direct"

# modes = ["Stimuli", "Dirac"]
# mode_stim = [5, 5]

modes = ["Stimuli"]
mode_stim = [5]

library = rir.Room("Library", 1.5, 1.2, 1.5, DRR=rir.DRR_adjustment_library)    # name, rt60, rd_ratio, mic_height, mic_distance
trapezoid = rir.Room("Trapezoid", 0.9, 1.2, 1.2, DRR=rir.DRR_adjustment_trapezoid)
rooms = [library, trapezoid]
root = "./.."

Direct = True
MP = False
FOA = False
HOA = False
SDM = False

gain = 1
compensated = True

def write_source(file, num, pos, name, location, vol, vol_db, slider_pos=45):
    file.write("\t<Source%d_x>%.9f</Source%d_x>\n" % (num, pos[0], num))
    file.write("\t<Source%d_y>%.9f</Source%d_y>\n" % (num, pos[1], num))
    file.write("\t<Source%d_z>%.9f</Source%d_z>\n" % (num, pos[2], num))
    file.write("\t<Source%d_vol>%.9f</Source%d_vol>\n" % (num, vol, num))
    file.write("\t<Source%d_vol_dB>%.9f</Source%d_vol_dB>\n" % (num, vol_db, num))
    file.write("\t<Source%d_sliderPosition>%d</Source%d_sliderPosition>\n" % (num, slider_pos, num))
    file_path = location + "/" + name + ".wav"
    file.write("\t<Source_%d_filePath>%s</Source_%d_filePath>\n" % (num, file_path, num))


for room in rooms:
    for ind, mode in enumerate(modes):

        num_sources = Direct * mode_stim[ind] + MP * mode_stim[ind] + FOA * 6 + HOA * 20 + SDM * 20

        source = 0
        xml_filename = xml_name_base + "_" + room.name + "_" + mode + ".xml"
    
        xml = open(os.path.join("C:\\Users\\craig\\Documents\\RIR_Project\\Audio_files\\Stimuli\\XML", xml_filename), "w+")
    
        xml.write("<BinauralApp>\n"
                  "\t<ListenerPosX>0.000000000</ListenerPosX>\n"
                  "\t<ListenerPosY>0.000000000</ListenerPosY>\n"
                  "\t<ListenerPosZ>0.000000000</ListenerPosZ>\n"
                  "\t<ListenerOrX>-0.000000000</ListenerOrX>\n"
                  "\t<ListenerOrY>-0.000000000</ListenerOrY>\n"
                  "\t<ListenerOrZ>0.000000000</ListenerOrZ>\n"
                  "\t<ListenerOrW>1.000000000</ListenerOrW>\n"
                  "\t<Platform>Mac</Platform>\n"
                  "\t<OSCListenPort>12300</OSCListenPort>\n"
                  "\t<BRIRPath>/Users/isaacengel/Box/Papers/Reverb study/Audio_files/BRIR/BRIR_%s_44100Hz.sofa</BRIRPath>\n"
                  "\t<HRTFPath>/Users/isaacengel/Box/Papers/Reverb study/Audio_files/HRTF/D2_44kHz_16bit_256tap_FIR_ITDextracted_norm_0dB.sofa</HRTFPath>\n"
                  "\t<NumSources>%d</NumSources>\n" % (room.name,num_sources))

        
        if Direct is True:
            if mode is "Stimuli":
                positions = [30, 0, 0, 0, 330]
                names = ['Piano', 'Ride', 'Kick', 'Snare', 'Sax']
            elif mode is "Dirac":
                positions = [30, 0, 0, 0, 330]
                names = ['Dirac', 'Dirac', 'Dirac', 'Dirac', 'Dirac']

            location = root + "/Dry"
            distance = room.mic_distance
            vol = gain / len(positions)
            vol_db = 20 * np.log(gain / len(positions))

            for ind, pos in enumerate(positions):
                cart = rir.spherical_2_cartesian(distance, 0, pos)
                write_source(xml, source, cart, names[ind], location, vol, vol_db)
                source += 1
                xml.write("\n")
                
        if MP is True:
            if mode is "Stimuli":
                positions = [30, 0, 0, 0, 330]
                names = ["%s_MP_%d" % (room.name, i) for i in range(len(positions))]
            elif mode is "Dirac":
                positions = [30, 0, 0, 0, 330]
                names = ["%s_MP_Dirac_%d" % (room.name, i) for i in range(len(positions))]
            location = root + "/MP"
            distance = room.mic_distance
            if compensated:
                vol = room.DRR[0][0] * gain
                vol_db = room.DRR[0][1] + 20 * np.log(gain)
            else:
                vol = gain
                vol_db = np.log(gain)

            for ind, pos in enumerate(positions):
                cart = rir.spherical_2_cartesian(distance, 0, pos)
                write_source(xml, source, cart, names[ind], location, vol, vol_db)
                source += 1
                xml.write("\n")
        
        if FOA is True:
            positions = [[0, 0],
                         [90, 0],
                         [180, 0],
                         [270, 0],
                         [0, 90],
                         [0, -90]]
            if mode is "Stimuli":
                names = ["%s_FOA_%d" % (room.name, i) for i in range(len(positions))]
            elif mode is "Dirac":
                names = ["%s_FOA_Dirac_%d" % (room.name, i) for i in range(len(positions))]

            location = root + "/FOA"
            distance = room.mic_distance
            if compensated:
                vol = room.DRR[1][0] * gain
                vol_db = room.DRR[1][1] + 20 * np.log(gain)
            else:
                vol = gain
                vol_db = np.log(gain)

            for ind, pos in enumerate(positions):
                cart = rir.spherical_2_cartesian(distance, pos[1], pos[0])
                write_source(xml, source, cart, names[ind], location, vol, vol_db)
                source += 1
                xml.write("\n")
        
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
            if mode is "Stimuli":
                names = ["%s_HOA_%d" % (room.name, i) for i in range(len(positions))]
            elif mode is "Dirac":
                names = ["%s_HOA_Dirac_%d" % (room.name, i) for i in range(len(positions))]
            location = root + "/HOA"
            distance = room.mic_distance

            if compensated:
                vol = room.DRR[2][0] * gain
                vol_db = room.DRR[2][1] + 20 * np.log(gain)
            else:
                vol = gain
                vol_db = np.log(gain)

            for ind, pos in enumerate(positions):
                write_source(xml, source, pos, names[ind], location, vol, vol_db)
                source += 1
                xml.write("\n")
        
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
            if mode is "Stimuli":
                names = ["%s_SDM_%d" % (room.name, i) for i in range(len(positions))]
            elif mode is "Dirac":
                names = ["%s_SDM_Dirac_%d" % (room.name, i) for i in range(len(positions))]
            location = root + "/SDM"
            distance = room.mic_distance

            if compensated:
                vol = room.DRR[3][0] * gain
                vol_db = room.DRR[3][1] + 20 * np.log(gain)
            else:
                vol = gain
                vol_db = np.log(gain)

            for ind, pos in enumerate(positions):
                write_source(xml, source, pos, names[ind], location, vol, vol_db)
                source += 1
                xml.write("\n")
        
        xml.write("</BinauralApp>")
        xml.close()