#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import lowtempcal


measurement_interval = 0.5

data = np.loadtxt('./rawdata/7V.csv', delimiter=',', dtype=lowtempcal.dtype)
data = data[::-1]
data['time'] = data['time']*measurement_interval

time = data['time']
temp = data['temperature']
volt = data['voltage']
current = data['current']

fig = plt.figure(figsize=(8,6))
ax = fig.add_subplot(211, axisbg='#FFFFCC')

ax.plot(time, temp, '-')
ax.set_title('Press left mouse button and drag to test')

ax2 = fig.add_subplot(212, axisbg='#FFFFCC')
line2, = ax2.plot(time, temp, '-')


def onselecttop(xmin, xmax):
    indmin, indmax = np.searchsorted(time, (xmin, xmax))
    indmax = min(len(time)-1, indmax)

    thisx = time[indmin:indmax]
    thisy = temp[indmin:indmax]
    line2.set_data(thisx, thisy)
    ax2.set_xlim(thisx[0], thisx[-1])
    ax2.set_ylim(thisy.min(), thisy.max())
    fig.canvas.draw()


def onselectbot(xmin, xmax):
    indmin, indmax = np.searchsorted(time, (xmin, xmax))
    indmax = min(len(time)-1, indmax)
    indmin = max(0, indmin)
    
    np.set_printoptions(precision=4)
    thisy = np.array(temp[indmin:indmax])
    ymean = np.mean(thisy, dtype=np.float64)
    ystd  = np.std(thisy)
    print("Temperature: {} ({})".format(ymean, ystd))

    p = lowtempcal.calc_radiated_power(ymean)
    print("Power: {}".format(p))

    i = np.mean(np.array(current[indmin:indmax]))
    v = np.mean(np.array(volt[indmin:indmax]))
    k = lowtempcal.calc_k(p, i, v, max(thisy)-min(thisy))
    print("Thermal Conductivity: {}\n".format(k))



span = SpanSelector(ax, onselecttop, 'horizontal', useblit=False,
                    rectprops=dict(alpha=0.5, facecolor='red') )
span2 = SpanSelector(ax2, onselectbot, 'horizontal', useblit=False,
                    rectprops=dict(alpha=0.1, facecolor='red') )


plt.show()

