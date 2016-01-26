import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.widgets import Slider, Button

dt = np.dtype([('time', np.float), ('temp', np.float)])
data = []

for i in range(3, 9):
    data.append(np.loadtxt('data/'+str(i)+'v.txt', delimiter=" "))
    print('loaded '+str(i)+'v.txt')

fig = plt.figure()

ax_graph = plt.axes([0.1, 0.2, 0.85, 0.7])
fig.add_axes(ax_graph)

ax_slider = plt.axes([0.1, 0.05, 0.7, 0.04])
fig.add_axes(ax_slider)
slider = Slider(ax_slider, 'V', 3, 8, 6, valfmt='%i')

ax_update = plt.axes([0.85, 0.05, 0.1, 0.04])
fig.add_axes(ax_update)
button_update = Button(ax_update, 'Update')

def updategraph(dummy=None):
    ax_graph.clear()
    ax_graph.plot(data[int(slider.val)-3][:,0], data[int(slider.val)-3][:,1])
    ax_graph.set_xlabel('Time / s')
    ax_graph.set_ylabel('Temperature / Celcius')
    ax_graph.set_title('low cal graph test')
    plt.draw()

button_update.on_clicked(updategraph)
updategraph()
plt.show()
