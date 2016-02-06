#!/usr/bin/env python

import numpy as np
import matplotlib as mpl
import scipy.stats as stat

import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import lowtempcal

from Tkinter import Tk
import tkFileDialog

plt.style.use('bmh')

filename = './7V.csv'
measurement_interval = 0.5

Tk().withdraw()
filename = tkFileDialog.askopenfile()

# filename = raw_input("File name: ")
# measurement_interval = np.float(raw_input("Time interval: "))

data = np.loadtxt(filename, delimiter=',', dtype=lowtempcal.dtype)
data = data[::-1]
data['time'] = data['time']*measurement_interval

time = data['time']
temp = data['temperature']
volt = data['voltage']
current = data['current']

fig = plt.figure(figsize=(8,6))
ax = fig.add_subplot(211, axisbg='#FFFFCC')

ax.plot(time, temp, '-')
ax.set_title('Press left mouse button and drag to zoom')
txt = ax.text(100,(max(temp)+min(temp))/2.0,'$T_{{\mathrm{{base}}}} = ?$\n'
                                            '$T_{{\mathrm{{max}}}} = ?$', size='xx-large')

ax2 = fig.add_subplot(212, axisbg='#FFFFCC')
ax2.set_title('Select area to to calculate base temperature')
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

stage = 0
blockenter = True
TBASE = 0
TMAX = 1
CV = 2
NSTAGES = 3

def calc_means(start,end):
    t = np.mean(np.array(temp[start:end]), dtype=np.float64)
    tstd  = np.std(np.array(temp[start:end]))
    i = np.mean(np.array(current[start:end]))
    v = np.mean(np.array(volt[start:end]))
    iv = np.mean(np.array(volt[start:end])*np.array(volt[start:end]))
    return t, tstd, i, v, iv

def onselectbot(xmin, xmax):
    global stage, blockenter
    global tempbase, tempbasestd, tempbasei, tempbasev
    global tempmax, tempmaxstd, tempmaxi, tempmaxv

    indmin, indmax = np.searchsorted(time, (xmin, xmax))
    indmax = min(len(time)-1, indmax)
    indmin = max(0, indmin)

    blockenter = False
    if stage == TBASE:
        tempbase, tempbasestd, tempbasei, tempbasev, tempbaseiv = calc_means(indmin,indmax)
        print("Temperature (base): {:.2f} ({:.2f})".format(tempbase, tempbasestd))
        print("(If that selection of the base temperature was wrong press enter to reselect)\n")
        txt.set_text("$T_{{\mathrm{{base}}}} = {:.2f} ({:.2f})$\n"
                     "$T_{{\mathrm{{max}}}} =  ?$".format(tempbase, tempbasestd))
        ax2.set_title('Select area to to calculate max temperature and thermal conductivity')

    elif stage == TMAX:
        tempmax, tempmaxstd, tempmaxi, tempmaxv, tempmaxiv = calc_means(indmin,indmax)
        p = lowtempcal.calc_radiated_power(tempmax)
        k = lowtempcal.calc_thermal_conductivity(p, tempmaxiv, tempmax-tempbase)
        print("Temperature (max): {:.2f} ({:.2f})".format(tempmax, tempmaxstd))
        print("(If that selection of the max temperature was wrong press enter to reselect)\n")

        print("Temperature (base): {:.2f} ({:.2f})".format(tempbase, tempbasestd))
        print("Temperature (max): {:.2f} ({:.2f})".format(tempmax, tempmaxstd))
        print("Power: {:.2g}".format(p))
        print("Thermal Conductivity: {:.2f}\n\n".format(k))
        txt.set_text("$T_{{\mathrm{{base}}}} = {:.2f} ({:.2f})$\n"
                     "$T_{{\mathrm{{max}}}} = {:.2f} ({:.2f})$"
                     .format(tempbase, tempbasestd, tempmax, tempmaxstd))
        ax2.set_title('Select area to perform linear regression on')
    elif stage == CV:
        slope, intercept, r_value, p_value, std_err = stat.linregress(time[indmin:indmax], temp[indmin:indmax])
        txt.set_text("$T_{{\mathrm{{base}}}} = {:.2f} ({:.2f})$\n"
                     "$T_{{\mathrm{{max}}}} = {:.2f} ({:.2f})$\n"
                     "$\\frac{{dT}}{{dt}}|_\\kappa = {:.4f} ({:.6f})$"
                     .format(tempbase, tempbasestd, tempmax, tempmaxstd, slope, std_err))
        print("Gradient between {:.0f} and {:.0f}: {:.4f} ({:.6f})"
                .format(xmin, xmax, slope, std_err))
        stage -= 1 # don't continue


    fig.canvas.draw()
    stage += 1
    stage %= NSTAGES


def onkeypress(event):
    global stage, blockenter, ax2
    if event.key == u'enter' and not blockenter:
        blockenter = True
        if stage == TMAX:
            ax2.set_title('Select area to to calculate base temperature')
            txt.set_text("$T_{{\mathrm{{base}}}} =  ?$\n"
                         "$T_{{\mathrm{{max}}}} =  ?$")
        elif stage == CV:
            txt.set_text("$T_{{\mathrm{{base}}}} = {:.2f} ({:.2f})$\n"
                         "$T_{{\mathrm{{max}}}} =  ?$".format(tempbase, tempbasestd))
            ax2.set_title('Select area to to calculate max temperature and thermal conductivity')
        elif stage == TBASE:
            return

        stage -= 1
        stage %= NSTAGES

        fig.canvas.draw()


span = SpanSelector(ax, onselecttop, 'horizontal', useblit=False, rectprops=dict(alpha=0.5, facecolor='black') )
span2 = SpanSelector(ax2, onselectbot, 'horizontal', useblit=False, rectprops=dict(alpha=0.3, facecolor='black') )
cid = fig.canvas.mpl_connect('key_release_event', onkeypress)

plt.show()

