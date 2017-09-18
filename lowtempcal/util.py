import os.path
import numpy as np
import scipy.constants as const
from matplotlib.lines import Line2D


def calc_radiated_power(temp, surface_area=1.0187e-3, emissivity=4e-2):
    return surface_area * emissivity * const.Stefan_Boltzmann * (temp**4)


def calc_thermal_conductivity(power, current, voltage, temp_diff,
                              surface_area=5.655e-7, length=0.01):
    return length*(np.abs(current)*voltage-power)/(surface_area*temp_diff)


class LowTempCalData:

    dtype = np.dtype([('time', np.int), ('current', np.float),
                      ('voltage', np.float), ('temperature', np.float)])

    def __init__(self, filename, binary=False):
        self.filename = filename
        self.basename = os.path.basename(filename)
        self.voltage = 5
        self.length = 0.01
        self.area = 1.0187e-3
        self.dt = 1

        self.power = 0
        self.kt = 0

        self.tmin_x1 = 0
        self.tmin_x2 = 0
        self.tmin = 0
        self.tmin_std = 0

        self.tmax_x1 = 0
        self.tmax_x2 = 0
        self.tmax = 0
        self.tmax_std = 0

        if binary:
            data = np.fromfile(filename, dtype=self.dtype)
        else:
            data = np.loadtxt(filename, delimiter=',',
                              dtype=LowTempCalData.dtype)[::-1]

        self.time = np.array(data['time'])
        self.temp = np.array(data['temperature'])
        self.current = np.abs(np.array(data['current']))
        self.line = Line2D(self.time, self.temp, label=self.basename,
                           visible=False)
        self.line_current = Line2D(self.time, self.current, label=self.basename,
                                   visible=False, color="red")
