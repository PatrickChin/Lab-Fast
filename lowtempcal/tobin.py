import os
import numpy as np

dtype = np.dtype([('time',np.int), ('current',np.float),
    ('voltage',np.float), ('temperature',np.float)])

os.mkdir("binary_data")
for f in os.listdir("./data"):
    data = np.loadtxt("./data/"+f, delimiter=',', dtype=dtype)[::-1]
    f = os.path.basename(f)
    f = os.path.splitext(f)[0]
    data.tofile("./binary_data/"+f)
