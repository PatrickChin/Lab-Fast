# Author - Adam Knoetze

import numpy as np
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import random
# import mpld3

# disable toolbar
matplotlib.rcParams['toolbar'] = 'None'

def muon_decay_n(t, tau, background, a):
    """Function to generate a number (non-int) of recorded muon decay events.
    Input:
        t - time /ns
        tau - mean muon lifetime /ns
        background - background count /N can be non integer
        a - constant /no-units
    Return:
        n - Count /Number calculated here as non-int"""
    n = background + (a*np.exp(-t/tau))
    return n


def gen_bins(minbin, maxbin, no):
    """Function to generate an array of time binns with a specified width.
    Input:
        minbin - smallest bin /ns
        maxbin - largest bin /ns
        no - number of bins 
    Return:
        bins - array of bins"""
    bins = np.linspace(minbin, maxbin, no)
    return bins


def fill_bins_fit(bins, tau, background, a, hv, bincount):
    """Function to generate an array of binned muon decay events for specific time bins
    in accordance the theoretical equation for muon decay events.
    Input:
        bins - array of time bins /ns
        tau - mean moun lifetime /ns
        background - background count /N can be non integer
        a - constant /no-units
        hv - High voltage /V
        bincount - Number of bins in histogram /Integer(not strict)
    Return:
        fitted - array of binned muon events that follow the theoretical equation"""
    fitted = []
    for t in bins:
        n = muon_decay_n(t, tau, background, a)
        n *= hv_adjustment(hv)
        n *= bin_adjustment(bincount)
        fitted.append(n)
    return fitted


def fill_bins_random(bins, deviation, tau, background, a, hv, bincount):
    """Function to generate an array ofrandom binned count values with
    a gaussian distributioncentred around the theoretical fitted equation.
    Input:
        bins - array of time bins /ns
        deviation - gaussian deviation
        tau - mean moun lifetime /ns
        background - background count /N can be non integer
        a - constant /no-units
        hv - High voltage /V
        bincount - Number of bins in histogram /Integer(not strict)
    Return:
        rand - An array of random muon counts /Integer"""
    rand = []
    for t in bins:
        r = muon_decay_n(t, tau, background, (a*(1 + random.gauss(0, deviation))))
        r *= hv_adjustment(hv)
        r *= bin_adjustment(bincount)
        rand.append(round(r, 0))
    return rand


def threshold_adjusted_tau(tau, threshold):
    """Function to adjust the mean muon lifetime to account for the threshold setting.
    Input:
        tau - mean moun lifetime /ns
        threshold - the chosen theshold value /V
    Return:
        tau - Adjustd mean muon lifetime /ns"""
    if threshold <= tau:
        tau *= (0.095/threshold)**2
    else:
        tau *= (threshold/0.095)**2
    return tau


def hv_adjustment(hv):
    """Function to generate the scalar value to adjust muon event counts by
    in relation to the HV setting.
    Input:
        hv - High voltage setting /V
    Return:
        adj - Scalar /no-units"""
    adj = (hv/10.01)
    return float(adj)


def bin_adjustment(bincount):
    """Function to generate the scalar value to adjust muon event counts by
    in relation to the number of bins in the in the histogram.
    Input:
        bincount - Number of bins in histogram /Integer(not strict althougth should be)
    Return:
        adj - Scalar /no-units"""
    adj = (100/float(round(bincount, 0)))
    return float(adj)


# initial contstants
tau = 2110  # mean lifetime
b = 0.3  # background
a = 65  # A constant
dev = 0.25  # deviation
threshold = 0.095  # in V
hv = 10.01  # in V
bincinit = 100 # initital number of bins

# generate initial arrays
t1 = gen_bins(100, 20000, bincinit)
n1 = fill_bins_fit(t1, threshold_adjusted_tau(tau, threshold), b, a, hv, bincinit)
r1 = fill_bins_random(t1, dev, threshold_adjusted_tau(tau, threshold), b, a, hv, bincinit)

# plot initialisation and styling
sns.set_style("whitegrid")
fig1 = plt.figure(1)
fig1.canvas.set_window_title('Muon Lifetime Experiment Simulation') 
ax = plt.subplot(111)
plt.subplots_adjust(bottom=0.3)

# plot data
line, = plt.plot(t1, n1, c='red')
scat, = plt.plot(t1, r1, '.k')

# adjust limits
plt.xlim(0, max(t1)+100)
plt.ylim(0, max(r1)+2)

# plot titles
plt.ylabel('Frequency N', fontsize=15)
plt.xlabel('Muon Lifetime t (ns)', fontsize=15)
plt.title('Binned Muon Lifetime Simulation', fontsize=20)

# add sliders
axhv = plt.axes([0.15, 0.1, 0.65, 0.03], axisbg='lightgoldenrodyellow')
axthreshold = plt.axes([0.15, 0.15, 0.65, 0.03], axisbg='lightgoldenrodyellow')
axbins = plt.axes([0.15, 0.05, 0.65, 0.03], axisbg='lightgoldenrodyellow')
shv = Slider(axhv, 'HV', 0.01, 20.00, valinit=9.50, valfmt='%1.2f V')
sthreshold = Slider(axthreshold, 'Threshold', 0.001, 0.500, valinit=0.240, valfmt='%1.3f V')
sbins = Slider(axbins, 'Bin Count', 50, 400, valinit=215, valfmt='%0.0f')

# add values to plot
txt = ax.text(20000, max(r1)-4, '$\\tau$ = ?', bbox=dict(facecolor='red', alpha=0.5), horizontalalignment='right', fontsize=20)
dsum = ax.text(20000, max(r1)-13, 'Total Decays = ?', bbox=dict(facecolor='red', alpha=0.5), horizontalalignment='right', fontsize=20)


def update(val):
    """Function which updates plot if slider positions are changed"""
    t1 = gen_bins(100, 20000, sbins.val)
    n1 = fill_bins_fit(t1, threshold_adjusted_tau(tau, sthreshold.val), b, a, shv.val, sbins.val)
    r1 = fill_bins_random(t1, dev, threshold_adjusted_tau(tau, sthreshold.val), b, a, shv.val, sbins.val)
    line.set_xdata(t1)
    line.set_ydata(n1)
    scat.set_xdata(t1)
    scat.set_ydata(r1)
    tadj = threshold_adjusted_tau(tau, sthreshold.val)*hv_adjustment(shv.val)*bin_adjustment(sbins.val)
    txt.set_text('$\\tau$ = {} ns'.format(str(tadj)))
    dsumval = int(np.sum(r1))
    dsum.set_text('Total Decays = {}'.format(dsumval))
    plt.draw()


# update plot
shv.on_changed(update)
sthreshold.on_changed(update)
sbins.on_changed(update)

# Lines to generate html fig of plot
# mpld3.show()
# fightml = mpld3.fig_to_html(fig)

# Show plot. Exeption handling for scenario when logo file cannot be reached.
try:
    from PIL import Image
    import urllib2
    import cStringIO
    file = cStringIO.StringIO(urllib2.urlopen("http://lab3vle.appspot.com/img/logos/logo-mulab-horizontal.png").read())
    img = Image.open(file)
    newax = fig1.add_axes([0.8, 0.9, 0.1, 0.1], anchor='NE')
    newax.imshow(img)
    newax.axis('off')
    plt.show()
except:
    plt.show()
