import numpy as np

dt = np.dtype([('decaytime', '<u4'), ('timestamp', '<u4')])
data = np.fromfile('datatest.bin', dtype=dt)

