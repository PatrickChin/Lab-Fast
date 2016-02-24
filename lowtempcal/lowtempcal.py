import os
import numpy as np
import scipy.constants as const
from PyQt5 import QtCore, QtWidgets

dtype = np.dtype([('time',np.int), ('current',np.float),
    ('voltage',np.float), ('temperature',np.float)])

class LowTempCalItem(QtWidgets.QListWidgetItem):

    def __init__(self, string, data, time_interval=1.0, parent=None):
        QtWidgets.QListWidgetItem.__init__(self, string, parent)
        self.data = data
        self.time_interval = time_interval

    @staticmethod
    def from_file(filename, parent=None):
        data = np.loadtxt(filename, delimiter=',', dtype=dtype)
        data = data[::-1]
        return LowTempCalItem(os.path.basename(filename), data, parent)

def calc_radiated_power(temp, surface_area=0.0010187, emissivity=0.04):
    return surface_area * emissivity * const.Stefan_Boltzmann * (temp**4)

def calc_thermal_conductivity(power, iv, temp_diff, surface_area=5.655e-7, length=0.01):
    return np.abs(length*(iv-power)/(surface_area*temp_diff))

def calc_thermal_conductivity2(power, current, voltage, temp_diff, surface_area=5.655e-7, length=0.01):
    return np.abs(length*(current*voltage-power)/(surface_area*temp_diff))

