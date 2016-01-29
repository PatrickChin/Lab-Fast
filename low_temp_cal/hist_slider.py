__author__ = "Patrick Chin"

LIVE_UPDATE_BINS=False

import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.widgets import Slider, Button
import scipy.stats as stats

class HistGraph:

    def __init__(self, ax, x_n=1000, x_avg=10, x_stdev=1, bins=10):
        self.x_n = x_n # number of points
        self.x_avg = x_avg # points avarage
        self.x_stdev = x_stdev

        self.bins = bins 
        self.recalc = False # does 'data' need to be recalculated?
        self.redraw = True # does histogram need to be redrawn?

        self.data = np.random.normal(self.x_avg, self.x_stdev, self.x_n) # create random data
        self.gauss_avg, self.gauss_stdev = stats.norm.fit(self.data)
        self.gauss_x = np.linspace(self.data.min(), self.data.max(), 100)
        self.gauss_y = stats.norm.pdf(self.gauss_x, self.gauss_avg, self.gauss_stdev)

        self.axes = ax # store axes

    def calc_data(self):
        if self.recalc: # recalculate data
            self.data = np.random.normal(self.x_avg, self.x_stdev, self.x_n)
            self.gauss_avg, self.gauss_stdev = stats.norm.fit(self.data)
            self.gauss_x = np.linspace(self.data.min(), self.data.max(), 100)
            self.gauss_y = stats.norm.pdf(self.gauss_x, self.gauss_avg, self.gauss_stdev)
            self.recalc = False # data recalculated
        return self.data, self.gauss_x, self.gauss_y

    def plot_graph(self):
        """(Re)draw histogram and gausian curve and labels on the stored graph axis"""
        if not self.redraw: return
        self.axes.clear()
        self.axes.hist(self.data, normed=True, bins=self.bins, alpha=0.25)
        self.axes.plot(self.gauss_x, self.gauss_y, label='Gauss')
        self.axes.set_ylim((0, 0.45))
        self.axes.set_xlabel('Measured Value')
        self.axes.set_ylabel('Probability Density')
        self.axes.set_title('Histogram Plot')
        plt.draw()
        self.redraw=False
        print("bins:{} n:{}".format(self.bins, self.x_n))

    def set_nbins(self, n):
        self.bins=int(n)
        self.redraw=True
        if LIVE_UPDATE_BINS: self.plot_graph()

    def set_nx(self, n):
        self.x_n=10**int(n)
        self.recalc=True
        self.redraw=True

    def update(self, n=None):
        self.calc_data()
        self.plot_graph()

fig = plt.figure()

### Create Graph Axes and HistGraph object
ax_graph = plt.axes([0.15, 0.25, 0.7, 0.7])
fig.add_axes(ax_graph)
graph = HistGraph(ax_graph)

### Number of Bins Slider
ax_slider_bin = plt.axes([0.15, 0.10, 0.5, 0.03])
fig.add_axes(ax_slider_bin)
slider_bin = Slider(ax_slider_bin, 'Bins', 1, 100, graph.bins, valfmt='%i')
slider_bin.on_changed(graph.set_nbins)

### Number of Data Points Slider
ax_slider_nx = plt.axes([0.15, 0.05, 0.5, 0.03])
fig.add_axes(ax_slider_nx)
slider_nx = Slider(ax_slider_nx, 'Points', 0.6, 6.5, np.log10(graph.x_n), valfmt='10e%i')
slider_nx.on_changed(graph.set_nx)

### Update Button
# + Redraw histogram plot using updated number of bins
# + If the number of data points needed has changed new data is calculated
ax_update = plt.axes([0.75, 0.05, 0.1, 0.08])
fig.add_axes(ax_update)
button_update = Button(ax_update, 'Update')
button_update.on_clicked(graph.update)

graph.plot_graph()
plt.show()

