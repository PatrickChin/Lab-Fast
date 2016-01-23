import numpy as np

class muondata:

    def __init__(self, path):
        self.data = np.loadtxt(path, delimiter=" ")

        # if (path.endswith(".txt") or path.endswith(".dat")):
        #     self.data = np.loadtxt(path, delimiter=" ")

        #     # write to binary file
        #     if tobin:
        #         binpath = path[0:-3]+"bin"
        #         data.tofile(binpath)

        # elif (path.endswith(".bin")):
        #     dt = np.dtype([('decaytime', '<u4'), ('timestamp', '<u4')])
        #     self.data = np.fromfile(path, dtype=dt)

        # else:
        #     print("File should end in '.txt', '.dat' for ascii encoded files"
        #           "or '.bin' for a binary encoded file")

