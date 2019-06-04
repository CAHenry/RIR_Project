import os
import PyRIR as rir
import soundfile as sf
import numpy as np

library = rir.Room("Library", 1.5, 1.2, 1.5)    # name, rt60, rd_ratio, mic_height, mic_distance
trapezoid = rir.Room("Trapezoid", 0.9, 1.2, 1.2)
rooms = [library, trapezoid]

root_dir = "C:\\Users\\craig\\Documents\\RIR_Project\\Audio_files"

for room in rooms:
    filter_dirs = [os.path.join(root_dir, "Impulses", room.name, "Eigenmike", "FOA"),
                   os.path.join(root_dir, "Impulses", room.name, "Eigenmike", "HOA"),
                   os.path.join(root_dir, "Impulses", room.name, "Eigenmike", "SDM"),
                   os.path.join(root_dir, "Impulses", room.name, "Eigenmike", "MP"),
                   os.path.join(root_dir, "Impulses", room.name, "Kemar", "trimmed")
                   ]
    for filter_dir in filter_dirs:
        for file in os.listdir(filter_dir):
            if ".wav" in file:
                data, fs = sf.read(os.path.join(filter_dir, file))
            else:
                continue
            data_abs_summed = np.sum(np.abs(data), 0)
            normalise = np.amax(data_abs_summed)
            print(file, normalise)
            if normalise > 1:
                data = data / (np.sqrt(normalise))
            output_dir = os.path.join(filter_dir, "normalised")
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)
            # sf.write(os.path.join(output_dir, file), data, fs)


