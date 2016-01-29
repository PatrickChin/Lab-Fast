import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.widgets import Slider, Button

class LowTempGUI():

    def __init__(self):

        self.minv = 3
        self.maxv = 7
        self.initv = 3

        self.data = []
        for i in range(self.minv, self.maxv+1):
            self.data.append(np.loadtxt('data/'+str(i)+'v.txt', delimiter=" "))
            print('loaded '+str(i)+'v.txt')

        self.fig = plt.figure()
        
        self.ax_graph = plt.axes([0.1, 0.2, 0.85, 0.7])
        self.fig.add_axes(self.ax_graph)

        self.ax_slider = plt.axes([0.1, 0.05, 0.85, 0.04])
        self.fig.add_axes(self.ax_slider)
        self.slider = Slider(self.ax_slider, 'V', self.minv, self.maxv, self.initv, valfmt='%i')
        self.slider.on_changed(self.updategraph)
        self.slider.prev_val = -1
        self.updategraph(self.initv)

        self.ax_graph.set_xlabel('Time / s')
        self.ax_graph.set_ylabel('Temperature / Celcius')
        self.ax_graph.set_title('low cal graph test')

        self.connected = False
        self.fig.canvas.mpl_connect('key_press_event', self.connect_mouse_listener)
        self.fig.show()
        plt.show()

    def updategraph(self, val):
        if self.slider.prev_val == int(val): return
        self.slider.prev_val = int(val)
        self.ax_graph.clear()
        self.ax_graph.plot(self.data[int(val)-self.minv][:,0], self.data[int(val)-self.minv][:,1])
        self.ax_graph.set_xlim(0, 3000)
        self.ax_graph.set_ylim(75, 105)
        self.fig.canvas.draw()
        

    def printevt(self, event):
        if event.xdata != None:
            print('button={}, x={:.3f}, y={:.3f}'.format(event.button, event.xdata, event.ydata))

    def connect_mouse_listener(self, event):
        if event.key != ' ': return
        if self.connected:
            self.fig.canvas.mpl_disconnect(self.kpe)
            self.fig.canvas.mpl_disconnect(self.kre)
        else:
            self.kpe = self.fig.canvas.mpl_connect('button_press_event', self.printevt)
            self.kre = self.fig.canvas.mpl_connect('button_release_event', self.printevt)
        self.connected = not self.connected

LowTempGUI()

