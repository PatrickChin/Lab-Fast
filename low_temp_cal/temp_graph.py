import sys
import os
import matplotlib.pyplot as plt
from numpy import loadtxt
from matplotlib.widgets import Slider

class LowTempGUI():

    def __init__(self, path='.'):

        self.data = []
        self.files = [os.path.abspath(os.path.join(path, f)) for f in os.listdir(path)]
        print(self.files)
        for f in self.files:
            self.data.append(loadtxt(f, delimiter=","))
            print('loaded {}'.format(os.path.basename(f)))

        self.fig = plt.figure()
        
        self.ax_graph = plt.axes([0.1, 0.2, 0.85, 0.7])
        self.fig.add_axes(self.ax_graph)

        self.ax_slider = plt.axes([0.1, 0.05, 0.85, 0.04])
        self.fig.add_axes(self.ax_slider)
        self.slider = Slider(self.ax_slider, 'file', 0, len(self.files)-1, 0, valfmt='%i')
        self.slider.on_changed(self.updategraph)
        self.slider.prev_val = -1
        self.updategraph(0)

        self.connected = False
        self.fig.canvas.mpl_connect('key_press_event', self.connect_mouse_listener)
        self.fig.show()
        plt.show()

    def updategraph(self, val):
        if self.slider.prev_val == int(val): return
        self.slider.prev_val = int(val)
        self.ax_graph.clear()
        self.ax_graph.plot(self.data[int(val)][:,0], self.data[int(val)][:,3])
        # self.ax_graph.set_xlim(0, 3000)
        # self.ax_graph.set_ylim(75, 105)

        self.ax_graph.set_xlabel('Time / units??')
        self.ax_graph.set_ylabel('Temperature / Celcius')
        self.ax_graph.set_title(self.files[int(val)])

        self.fig.canvas.draw()
        

    def printevt(self, event):
        if event.inaxes != self.ax_graph: return
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

if __name__ == '__main__':
    # LowTempGUI(sys.argv[1])
    LowTempGUI('./rawdata/')

