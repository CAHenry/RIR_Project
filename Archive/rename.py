# imports
import PyRIR as rir

import os
import re
import soundfile as sf
from scipy import signal
import numpy as np

# Define directory, rooms and techniques

library = rir.Room("Library", 1.5, 1.5, 1.2)    # name, rt60, mic_height, mic_distance
trapezoid = rir.Room("Trapezoid", 0.9, 1.5, 1.2)
rooms = [library, trapezoid]

kemar = rir.Measurement("Kemar", ["0", "90", "180", "270", "top", "bottom"])
eigenmike = rir.Measurement("Eigenmike", [str(x) for x in range(0, 360, 10)])
methods = [kemar, eigenmike]

root_dir = "C:\\Users\\craig\\Documents\\RIR_Project\\Audio_files"


for room in rooms:
    for method in methods:

        sweep_dir = os.path.join(root_dir, "Sweeps", room.name, method.name)
        if not os.path.isdir(sweep_dir):
            os.makedirs(sweep_dir)

        for file_name in os.listdir(sweep_dir):

            if "top" in file_name:
                direction = "top"
            elif "bottom" in file_name:
                direction = "bottom"
            else:
                orig_direction = int(re.findall("\d+", file_name)[0])
                direction = str(np.mod(360 - orig_direction, 360))

            new_name = room.name + "_" + method.name + "_" + direction + "_Sweep.wav"

            os.rename(os.path.join(sweep_dir, file_name), os.path.join(sweep_dir, new_name))
