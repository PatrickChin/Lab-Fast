import sys
import numpy as np
import scipy.optimize as opt

def loaddata(filename):
    muondata = np.loadtxt(filename, delimiter=' ', dtype=int)


