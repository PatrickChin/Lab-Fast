import os
import numpy as np
from scipy import stats
import scipy.constants as const
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUiType

import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.lines import Line2D
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

class LowTempCalData:

    dtype = np.dtype([('time',np.int), ('current',np.float),
        ('voltage',np.float), ('temperature',np.float)])

    def __init__(self, filename):
        self.voltage = 1
        self.length = 1
        self.area = 1
        self.dt = 1

        self.tmin_x1 = 1
        self.tmin_x2 = 1
        self.tmin = 1
        self.tmin_std = 1

        self.tmax_x1 = 1
        self.tmax_x2 = 1
        self.tmax = 1
        self.tmax_std = 1

        self.data = np.loadtxt(filename, delimiter=',', dtype=LowTempCalData.dtype)[::-1]
        self.line = Line2D(self.data['time'], self.data['temperature'], label=os.path.basename(filename), visible=False)
        self.line_current = Line2D(self.data['time'], self.data['current'], label=os.path.basename(filename), visible=False, color="red")

Ui_MainWindow, QMainWindow = loadUiType('mainwindow.ui')

class LowTempCalValueGroup(QtWidgets.QWidget):

    def __init__(self, text, parent):
        # QtWidgets.QWidget.__init__(parent=parent)
        super().__init__()

        self.layout = QtWidgets.QFormLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)

        self.radio = QtWidgets.QRadioButton(text)
        self.radio.toggled.connect(self.setEnabled)

        self.label_start = QtWidgets.QLabel("Start", parent=self)
        self.label_start.setIndent(22)
        self.layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_start)

        self.start = QtWidgets.QSpinBox(self)
        self.layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.start)

        self.label_end = QtWidgets.QLabel("End", parent=self)
        self.label_end.setIndent(22)
        self.layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_end)

        self.end = QtWidgets.QSpinBox(self)
        self.end.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.end)

        self.labelue = QtWidgets.QLabel("Value", parent=self)
        self.labelue.setIndent(22)
        self.layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.labelue)

        self.value = QtWidgets.QDoubleSpinBox(self)
        self.value.setReadOnly(True)
        self.value.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.value)

        self.label_std = QtWidgets.QLabel("Std", parent=self)
        self.label_std.setIndent(22)
        self.layout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_std)

        self.std = QtWidgets.QDoubleSpinBox(self)
        self.std.setReadOnly(True)
        self.std.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.layout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.std)

        self.setEnabled(False)

    def setues(self, x1, x2, val, std):
        self.start.setValue(x1)
        self.end.setValue(x2)
        self.value.setValue(val)
        self.std.setValue(std)

def calc_radiated_power(temp, surface_area=1.0187e-3, emissivity=4e-2):
    return surface_area * emissivity * const.Stefan_Boltzmann * (temp**4)

def calc_thermal_conductivity(radiated_power, iv, temp_diff, surface_area=5.655e-7, length=0.01):
    return np.abs(length*(iv-radiated_power)/(surface_area*temp_diff))

def calc_thermal_conductivity2(power, current, voltage, temp_diff, surface_area=5.655e-7, length=0.01):
    return np.abs(length*(current*voltage-power)/(surface_area*temp_diff))


class LowTempCalApp(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.fig = Figure(facecolor="white")
        self.ax_current = self.fig.add_subplot(111, frameon=False)
        self.ax_temp = self.ax_current.twinx()
        self.canvas = FigureCanvas(self.fig)
        self.graph_layout.addWidget(self.canvas)
        self.canvas.draw()

        self.checkbox_show_current.stateChanged.connect(self.show_current_graph)

        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.graph_layout.addWidget(self.toolbar)
 
        self.prev_dir = '.'
        self.file_import_button.clicked.connect(self.import_dialog)
        self.filenames = []
        self.data = []
        self.cur_index = 0

        self.file_list_box.currentIndexChanged.connect(self.file_change)

        self.tmax_group = LowTempCalValueGroup("Max Temperature", self.value_layout)
        self.value_layout.addRow(self.tmax_group.radio)
        self.value_layout.addRow(self.tmax_group)

        self.tmin_group = LowTempCalValueGroup("Min Temperature", self.value_layout)
        self.value_layout.addRow(self.tmin_group.radio)
        self.value_layout.addRow(self.tmin_group)

        self.tmax_group.radio.toggle()

        self.span = SpanSelector(self.ax_temp, self.on_span_select, 'horizontal', useblit=False,
                span_stays=False, rectprops=dict(alpha=0.1, facecolor='blue') )

    def show_current_graph(self, state):
        print("state: {}".format(state))
        if state:
            self.ax_current.set_axis_off()
        else:
            self.ax_current.set_axis_on()


    def on_span_select(self, x1, x2):
        d = self.data[self.cur_index]
        x1 = max(0, int(x1/d.dt))
        x2 = min(len(d.data)-1, int(x2/d.dt))
        temp = d.data['temperature'][x1:x2]
        time = d.data['time'][x1:x2]
        if self.tmax_group.radio.isChecked():
            val = np.mean(temp)
            std = np.std(temp)
            self.tmax_group.setues(x1, x2, val, std)
            d.tmax_x1 = x1
            d.tmax_x2 = x2
            d.tmax = val
            d.tmax_std = std
        elif self.tmin_group.radio.isChecked():
            val = np.mean(temp)
            std = np.std(temp)
            self.tmin_group.setues(x1, x2, val, std)
            d.tmin_x1 = x1
            d.tmin_x2 = x2
            d.tmin = val
            d.tmin_std = std

        # Only calculate for a temperature change larger than 0.1 degrees
        dtemp = d.tmax - d.tmin 
        if dtemp > 0.1:
            power = calc_radiated_power(d.tmax) # , self.spinbox_area.value())
            current = np.mean(d.data['current'][d.tmax_x1:d.tmax_x2])
            d.voltage = self.spinbox_voltage.value()
            d.kt = calc_thermal_conductivity(power, current*d.voltage, dtemp) #, self.spinbox_area.value(), self.spinbox_len.value())
            self.spinbox_kt.setValue(d.kt)

    def file_change(self, index):
        self.cur_index = index
        if len(self.data) < 1:
            return

        for i, d in enumerate(self.data):
            d.line_current.set_visible(i == index and self.checkbox_show_current.isChecked())
            d.line.set_visible(i == index)
        self.ax_current.relim(True)
        self.ax_current.autoscale()
        self.ax_temp.relim(True)
        self.ax_temp.autoscale()
        self.canvas.draw()

        d = self.data[index]
        self.tmax_group.setues(d.tmax_x1, d.tmax_x2, d.tmax, d.tmax_std)
        self.tmin_group.setues(d.tmin_x1, d.tmin_x2, d.tmin, d.tmin_std)

        ld = len(d.data)
        self.tmax_group.start.setMaximum(ld)
        self.tmin_group.start.setMaximum(ld)
        self.tmax_group.end.setMaximum(ld)
        self.tmin_group.end.setMaximum(ld)

    def import_dialog(self):
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
                self, 'Select one or more data files to import', directory=self.prev_dir)
        if len(filenames) < 1:
            return
        self.import_files(filenames)

    def import_files(self, filenames):
        print(self.filenames)
        for f in filenames:
            f = os.path.abspath(f)
            if f in self.filenames:
                print('Not importing \"{}\", it was already imported'.format(f))
                continue
            print("Adding \"{}\"".format(f))
            self.filenames.append(f)
            self.file_list_box.addItem(os.path.basename(f))
            item = LowTempCalData(f)
            self.data.append(item)
            self.ax_temp.add_line(item.line)
            self.ax_current.add_line(item.line_current)
            self.canvas.draw()


if __name__ == '__main__':
    import sys
 
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyle("breeze")
    main = LowTempCalApp()
    main.import_files([
        './data/2V',
        './data/3V',
        './data/4V',
        './data/5V'
    ])
    main.file_change(0)

    main.show()
    sys.exit(app.exec_())

