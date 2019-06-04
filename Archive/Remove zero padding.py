import soundfile as sf
import os

rootdir = "C:\\Users\\craig\\Documents\\RIR_Project\\Audio_files\\Impulses"

for folder, subs, files in os.walk(rootdir):
    for filename in files:
        full_path = os.path.join(folder, filename)
        data, fs = sf.read(full_path)
        data = data[268:]
        print(data.shape)
        # sf.write(data, full_path, fs)

