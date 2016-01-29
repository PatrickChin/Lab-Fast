import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.widgets import Slider, Button

class LowTempGUI():

    def __init__(self):
        self.fig = plt.figure()
        
        self.fig.add_axes(ax_graph)

        ax_graph = plt.axes([0.1, 0.2, 0.85, 0.7])
        fig.add_axes(ax_graph)

        self.ax_slider = plt.axes([0.1, 0.05, 0.85, 0.04])
        self.fig.add_axes(ax_slider)
        self.slider = Slider(ax_slider, 'V', minv, maxv, initv, valfmt='%i')
        self.slider.prev_val = -1

        self.ax_graph.set_xlabel('Time / s')
        self.ax_graph.set_ylabel('Temperature / Celcius')
        self.ax_graph.set_title('low cal graph test')



minv = 3
maxv = 7
initv = 3

dt = np.dtype([('time', np.float), ('temp', np.float)])
data = []

for i in range(minv, maxv+1):
    data.append(np.loadtxt('data/'+str(i)+'v.txt', delimiter=" "))
    print('loaded '+str(i)+'v.txt')

fig = plt.figure()

ax_graph = plt.axes([0.1, 0.2, 0.85, 0.7])
fig.add_axes(ax_graph)

ax_slider = plt.axes([0.1, 0.05, 0.85, 0.04])
fig.add_axes(ax_slider)
slider = Slider(ax_slider, 'V', minv, maxv, initv, valfmt='%i')
slider.prev_val = -1


def updategraph(val):
    if slider.prev_val == int(val): return
    slider.prev_val = int(val)
    ax_graph.clear()
    ax_graph.plot(data[int(val)-minv][:,0], data[int(val)-minv][:,1])
    ax_graph.set_xlim(0, 2000)
    ax_graph.set_ylim(75, 105)
    plt.draw()
    
ax_graph.set_xlabel('Time / s')
ax_graph.set_ylabel('Temperature / Celcius')
ax_graph.set_title('low cal graph test')

def evnthandler(event):
    print('button={}, x={:.3f}, y={:.3f}'.format(event.button, event.xdata, event.ydata))

connected = False
kpe = None
kre = None
def connectlistener(e):
    if connected:
        fig.canvas.mpl_disconnect(kpe)
        fig.canvas.mpl_disconnect(kre)
    else:
        kpe = fig.canvas.mpl_connect('button_press_event', evnthandler)
        kre = fig.canvas.mpl_connect('button_release_event', evnthandler)

fig.canvas.mpl_connect('key_press_event', connectlistener)

slider.on_changed(updategraph)
updategraph(initv)
plt.show()
