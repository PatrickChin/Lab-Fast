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

    def tobin(self):
        self.data.tofile(os.path.splitext(self.path)[0]+".bin")

    def analyse(self, bins=20, range=None, normed=False, weights=None, density=None):
        self.hist, self.bin_edges = np.histogram(self.data['decaytime'], bins, range, normed, weights, density)
        self.mids = (self.bin_edges[1:] + self.bin_edges[:-1]) / 2

    def plot(self, logy=True):
        plt.plot(self.mids, self.hist, '+')
        plt.grid(True, which='both')
        if logy:
            plt.yscale('log')
        plt.xlabel('Decay time (ns)')
        plt.ylabel('Counts per bin')
        plt.show()


m = muondata('data.bin', True)
m.analyse()
m.plot()
