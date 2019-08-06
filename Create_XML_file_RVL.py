import os
import PyRIR as rir
import numpy as np

xml_name_base = "RVL_4OA"

frame_size = 256
reverb_order = "0D"

# modes = ["TakeFive"]#,"Speech"]
# mode_stim = [5]#,1]

# modes = ["TakeFive"]
# mode_stim = [5]

modes = ["Dirac1"]
mode_stim = [1]

library = rir.Room("Library", 1.5, 1.2, 1.5, DRR=rir.DRR_adjustment_library)  # name, rt60, rd_ratio, mic_height, mic_distance
trapezoid = rir.Room("Trapezoid", 0.9, 1.2, 1.2, DRR=rir.DRR_adjustment_trapezoid)
rooms = [library,trapezoid]
root = "./.."

Direct = False
MP = False
SDM = False
_0OA = False
_1OA = False
_2OA = False
_3OA = False
_4OA = False
_1OA_s = False
RVL_4OA = True

gain = 1.0
compensated = False
reverbPlus6db = False  # whether to add 6db to all reverbs, to make the listening test easier

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

num_sources = 32

IRpos_vec = ['0','180','90','270','bottom','top']

for IRpos in IRpos_vec:

    for room in rooms:

        source = 0
        xml_filename = xml_name_base + "_" + room.name + "_" + IRpos + ".xml"

        #xml = open(os.path.join("C:\\Users\\craig\\Documents\\RIR_Project\\Audio_files\\Stimuli\\XML", xml_filename), "w+")
        xml = open(os.path.join("C:\\Users\\Isaac\\Audio_files\\Stimuli\\XML",xml_filename), "w+")
        #xml = open(os.path.join("/Users/isaacengel/Documents/Audio_files/Stimuli/XML", xml_filename), "w+")

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
                  #"\t<BRIRPath>/Users/isaacengel/Documents/Audio_files/BRIR/BRIR_%s_44100Hz_Normalised.sofa</BRIRPath>\n"
                  #"\t<HRTFPath>/Users/isaacengel/Documents/Audio_files/HRTF/D2_44kHz_16bit_256tap_FIR_ITDextracted_norm_0dB.sofa</HRTFPath>\n"
                  "\t<ReverbOrder>%s</ReverbOrder>\n"
                  "\t<NumSources>%d</NumSources>\n" % (frame_size,reverb_order,num_sources))

        for mode in modes:


            if RVL_4OA is True:
                positions = rir.pentakis_dodec
                names = ["%s_RVL_4OA_%s_%s_%d" % (room.name, mode, IRpos, i) for i in range(len(positions))]
                location = root + "/RVL_4OA"
                distance = room.mic_distance

                if compensated:
                    vol = 10**(room.DRR[6]/20) * gain
                else:
                    vol = gain
                if reverbPlus6db:
                    vol = 2*vol
                vol_db = 20 * np.log10(vol)

                for ind, pos in enumerate(positions):
                    cart = rir.spherical_2_cartesian(distance, pos[1], pos[0])
                    write_source(xml, source, cart, names[ind], location, vol, vol_db)
                    source += 1
                    xml.write("\n")

        xml.write("</BinauralApp>")
        xml.close()
