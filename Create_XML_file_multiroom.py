import os
import PyRIR as rir
import numpy as np

xml_name_base = "Fullfull"

frame_size = 256
reverb_order = "0D"

modes = ["TakeFive", "Speech"]
mode_stim = [5, 1]

library = rir.Room("Library", 1.5, 1.2, 1.5, DRR=rir.DRR_adjustment_library)    # name, rt60, rd_ratio, mic_height, mic_distance
trapezoid = rir.Room("Trapezoid", 0.9, 1.2, 1.2, DRR=rir.DRR_adjustment_trapezoid)
rooms = [library, trapezoid]
root = "./.."

Direct = True
MP = False
FOA = False
HOA = False
SDM = False
_0OA = True
_1OA = True
_2OA = True
_3OA = True
_4OA = True

gain = 1
compensated = True

def write_source(file, num, pos, name, location, vol, vol_db, slider_pos=45, reverb_state="Off"):
    file.write("\t<Source%d_x>%.9f</Source%d_x>\n" % (num, pos[0], num))
    file.write("\t<Source%d_y>%.9f</Source%d_y>\n" % (num, pos[1], num))
    file.write("\t<Source%d_z>%.9f</Source%d_z>\n" % (num, pos[2], num))
    file.write("\t<Source%d_vol>%.9f</Source%d_vol>\n" % (num, vol, num))
    file.write("\t<Source%d_vol_dB>%.9f</Source%d_vol_dB>\n" % (num, vol_db, num))
    file.write("\t<Source%d_sliderPosition>%d</Source%d_sliderPosition>\n" % (num, slider_pos, num))
    file_path = location + "/" + name + ".wav"
    file.write("\t<Source_%d_filePath>%s</Source_%d_filePath>\n" % (num, file_path, num))
    file.write("\t<Source_%d_reverb>%s</Source_%d_reverb>\n" % (num, reverb_state, num))
    file.write("\t<Source_%d_NF>Off</Source_%d_NF>\n" % (num, num))
    file.write("\t<Source_%d_FD>Off</Source_%d_FD>\n" % (num, num))

num_sources = 0
for ind, mode in enumerate(modes):
    num_sources += len(rooms) * (Direct*mode_stim[ind] + MP*mode_stim[ind] + SDM*20 + _0OA*6 + _1OA*6 + _2OA*12 + _3OA*20 + _4OA*32)

xml_filename = xml_name_base + ".xml"

# xml = open(os.path.join("C:\\Users\\craig\\Documents\\RIR_Project\\Audio_files\\Stimuli\\XML", xml_filename), "w+")
xml = open(os.path.join("C:\\Users\\Isaac\\Audio_files\\Stimuli_EQ\\XML", xml_filename), "w+")
# xml = open(os.path.join("/Users/isaacengel/Documents/Audio_files/Stimuli/XML", xml_filename), "w+")

xml.write("<BinauralApp>\n"
          "\t<FrameSize>%d</FrameSize>\n"
          "\t<ListenerPosX>0.000000000</ListenerPosX>\n"
          "\t<ListenerPosY>0.000000000</ListenerPosY>\n"
          "\t<ListenerPosZ>0.000000000</ListenerPosZ>\n"
          "\t<ListenerOrX>-0.000000000</ListenerOrX>\n"
          "\t<ListenerOrY>-0.000000000</ListenerOrY>\n"
          "\t<ListenerOrZ>0.000000000</ListenerOrZ>\n"
          "\t<ListenerOrW>1.000000000</ListenerOrW>\n"
          "\t<Platform>Mac</Platform>\n"
          "\t<OSCListenPort>12300</OSCListenPort>\n"
          # "\t<BRIRPath>/Users/isaacengel/Documents/Audio_files/BRIR/BRIR_%s_44100Hz_0db.sofa</BRIRPath>\n"
          # "\t<HRTFPath>/Users/isaacengel/Documents/Audio_files/HRTF/D2_44kHz_16bit_256tap_FIR_ITDextracted_norm_0dB.sofa</HRTFPath>\n"
          "\t<ReverbOrder>%s</ReverbOrder>\n"
          "\t<NumSources>%d</NumSources>\n" % (
          frame_size, reverb_order, num_sources))  # room.name,reverb_order,num_sources))

source = 0

for mode in modes:

    for room in rooms:

        if Direct is True:
            if mode is "TakeFive":
                positions = [30, 0, 0, 0, 330]
                names = ['TakeFive_Piano', 'TakeFive_Ride', 'TakeFive_Kick', 'TakeFive_Snare', 'TakeFive_Sax']
            elif mode is "Dirac":
                positions = [30, 0, 0, 0, 330]
                names = ['Dirac', 'Dirac', 'Dirac', 'Dirac', 'Dirac']
            elif mode is "Speech":
                positions = [30]
                names = ['Speech']

            location = root + "/Dry"
            distance = room.mic_distance
            vol = gain / len(positions)
            vol_db = 20 * np.log10(vol)

            for ind, pos in enumerate(positions):
                cart = rir.spherical_2_cartesian(distance, 0, pos)
                write_source(xml, source, cart, names[ind], location, vol, vol_db)
                source += 1
                xml.write("\n")

        if MP is True:
            if mode is "TakeFive":
                positions = [30, 0, 0, 0, 330]
            elif mode is "Dirac":
                positions = [30, 0, 0, 0, 330]
            elif mode is "Speech":
                positions = [30]
            names = ["%s_MP_%s_%d" % (room.name, mode, i) for i in range(len(positions))]
            location = root + "/MP"
            distance = room.mic_distance

            if compensated:
                vol = room.DRR[6][0] * gain
            else:
                vol = gain
            vol_db = 20 * np.log10(vol)

            for ind, pos in enumerate(positions):
                cart = rir.spherical_2_cartesian(distance, 0, pos)
                write_source(xml, source, cart, names[ind], location, vol, vol_db)
                source += 1
                xml.write("\n")

        if SDM is True:
            positions = rir.mirrored_dodec
            names = ["%s_SDM_%s_%d" % (room.name, mode, i) for i in range(len(positions))]
            location = root + "/SDM"
            distance = room.mic_distance

            if compensated:
                vol = room.DRR[1][0] * gain
            else:
                vol = gain
            vol_db = 20 * np.log10(vol)

            for ind, pos in enumerate(positions):
                cart = rir.spherical_2_cartesian(distance, pos[1], pos[0])
                write_source(xml, source, cart, names[ind], location, vol, vol_db)
                source += 1
                xml.write("\n")

        if _0OA is True:
            positions = rir.tetrahedron
            names = ["%s_0OA_%s_%d" % (room.name, mode, i) for i in range(len(positions))]
            location = root + "/0OA"
            distance = room.mic_distance

            if compensated:
                vol = room.DRR[2][0] * gain
            else:
                vol = gain
            vol_db = 20 * np.log10(vol)

            for ind, pos in enumerate(positions):
                cart = rir.spherical_2_cartesian(distance, pos[1], pos[0])
                write_source(xml, source, cart, names[ind], location, vol, vol_db)
                source += 1
                xml.write("\n")

        if _1OA is True:
            positions = rir.tetrahedron
            names = ["%s_1OA_%s_%d" % (room.name, mode, i) for i in range(len(positions))]
            location = root + "/1OA"
            distance = room.mic_distance

            if compensated:
                vol = room.DRR[3][0] * gain
            else:
                vol = gain
            vol_db = 20 * np.log10(vol)

            for ind, pos in enumerate(positions):
                cart = rir.spherical_2_cartesian(distance, pos[1], pos[0])
                write_source(xml, source, cart, names[ind], location, vol, vol_db)
                source += 1
                xml.write("\n")

        if _2OA is True:
            positions = rir.icosahedron
            names = ["%s_2OA_%s_%d" % (room.name, mode, i) for i in range(len(positions))]
            location = root + "/2OA"
            distance = room.mic_distance

            if compensated:
                vol = room.DRR[4][0] * gain
            else:
                vol = gain
            vol_db = 20 * np.log10(vol)

            for ind, pos in enumerate(positions):
                cart = rir.spherical_2_cartesian(distance, pos[1], pos[0])
                write_source(xml, source, cart, names[ind], location, vol, vol_db)
                source += 1
                xml.write("\n")

        if _3OA is True:
            positions = rir.dodecahedron
            names = ["%s_3OA_%s_%d" % (room.name, mode, i) for i in range(len(positions))]
            location = root + "/3OA"
            distance = room.mic_distance

            if compensated:
                vol = room.DRR[5][0] * gain
            else:
                vol = gain
            vol_db = 20 * np.log10(vol)

            for ind, pos in enumerate(positions):
                cart = rir.spherical_2_cartesian(distance, pos[1], pos[0])
                write_source(xml, source, cart, names[ind], location, vol, vol_db)
                source += 1
                xml.write("\n")

        if _4OA is True:
            positions = rir.pentakis_dodec
            names = ["%s_4OA_%s_%d" % (room.name, mode, i) for i in range(len(positions))]
            location = root + "/4OA"
            distance = room.mic_distance

            if compensated:
                vol = room.DRR[6][0] * gain
            else:
                vol = gain
            vol_db = 20 * np.log10(vol)

            for ind, pos in enumerate(positions):
                cart = rir.spherical_2_cartesian(distance, pos[1], pos[0])
                write_source(xml, source, cart, names[ind], location, vol, vol_db)
                source += 1
                xml.write("\n")

xml.write("</BinauralApp>")
xml.close()
