import os
import numpy as np
from matplotlib import pyplot as plt

class muondata:

    def __init__(self, path, binary=False):
        self.path = path

        dt = np.dtype([('decaytime', np.uint32), ('timestamp', np.uint32)])
        if binary:
            self.data = np.fromfile(path, dtype=dt)
        else:
            self.data = np.loadtxt(path, delimiter=" ", dtype=dt)

        self.bgdata = self.data[self.data['decaytime'] >= 40000]
        self.data   = self.data[self.data['decaytime'] < 40000]

        self.analyse()



    def tobin(self):
        self.data.tofile(os.path.splitext(self.path)[0]+".bin")

    def analyse(self):
        self.hist = np.histogram(self.data['decaytime'])

    def plot(self):
        plt.plot(self.hist.index, self.hist.count)


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

m = muondata('data.bin', True)
