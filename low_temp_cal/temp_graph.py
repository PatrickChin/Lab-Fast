import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.widgets import Slider, Button

minv = 3
maxv = 8
initv = 5

dt = np.dtype([('time', np.float), ('temp', np.float)])
data = []

for i in range(minv, maxv):
    data.append(np.loadtxt('data/'+str(i)+'v.txt', delimiter=" "))
    print('loaded '+str(i)+'v.txt')

fig = plt.figure()

ax_graph = plt.axes([0.1, 0.2, 0.85, 0.7])
fig.add_axes(ax_graph)

ax_slider = plt.axes([0.1, 0.05, 0.85, 0.04])
fig.add_axes(ax_slider)
slider = Slider(ax_slider, 'V', minv, maxv, initv, valfmt='%i')
slider.prev_val = initv


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

slider.on_change(updategraph)
updategraph()
plt.show()
