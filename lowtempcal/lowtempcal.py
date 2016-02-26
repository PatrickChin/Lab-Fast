import os
import numpy as np
import scipy.constants as const
from PyQt4 import QtCore, QtGui
from PyQt4.uic import loadUiType
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

Ui_MainWindow, QMainWindow = loadUiType('mainwindow.ui')


def calc_radiated_power(temp, surface_area=0.0010187, emissivity=0.04):
    return surface_area * emissivity * const.Stefan_Boltzmann * (temp**4)

def calc_thermal_conductivity(power, iv, temp_diff, surface_area=5.655e-7, length=0.01):
    return np.abs(length*(iv-power)/(surface_area*temp_diff))

def calc_thermal_conductivity2(power, current, voltage, temp_diff, surface_area=5.655e-7, length=0.01):
    return np.abs(length*(current*voltage-power)/(surface_area*temp_diff))


class LowTempCalItem(QtGui.QListWidgetItem):

    dtype = np.dtype([('time',np.int), ('current',np.float),
        ('voltage',np.float), ('temperature',np.float)])

    def __init__(self, string, data, time_interval=1.0, parent=None):
        QtGui.QListWidgetItem.__init__(self, string, parent)
        self.data = data
        self.dt = time_interval
        self.line = None

    @staticmethod
    def from_file(filename, parent=None):
        data = np.loadtxt(filename, delimiter=',', dtype=LowTempCalItem.dtype)
        data = data[::-1]
        return LowTempCalItem(os.path.basename(filename), data, parent)


class LowTempCalApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(LowTempCalApp, self).__init__()
        self.setupUi(self)

        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.graph_layout.addWidget(self.canvas)
        self.canvas.draw()
 
        self.prev_dir = '.'
        self.file_import_button.clicked.connect(self.import_file)
        self.files = []

        self.button_select_all.clicked.connect(self.select_all)
        self.button_deselect_all.clicked.connect(self.deselect_all)
        self.button_replot.clicked.connect(self.replot)

    def replot(self):
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            show = item.checkState()
            item.line.set_visible(show)
        self.canvas.draw()

    def deselect_all(self):
        for i in range(self.file_list.count()):
            self.file_list.item(i).setCheckState(QtCore.Qt.Unchecked)

    def select_all(self):
        for i in range(self.file_list.count()):
            self.file_list.item(i).setCheckState(QtCore.Qt.Checked)

    def import_file(self):
        filenames = QtGui.QFileDialog.getOpenFileNames(
                self, 'Select one or more data files to import', directory=self.prev_dir)
        if len(filenames) < 1:
            return
        self.prev_dir = os.path.dirname(str(filenames[0]))
        for f in filenames: # unsure why this is an array of array
            f = str(f) # QString acts wierd

            if f in self.files:
                print('Not importing \"{}\", it was already imported'.format(f))
                break
            self.files.append(f)

            item = LowTempCalItem.from_file(f)
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Checked)
            line, = self.ax.plot(item.data['time'], item.data['temperature'])
            line.set_visible(False)
            item.line = line

            self.file_list.addItem(item)
            self.canvas.draw()


if __name__ == '__main__':
    import sys
 
    app = QtGui.QApplication(sys.argv)
    main = LowTempCalApp()
    main.show()
    sys.exit(app.exec_())

