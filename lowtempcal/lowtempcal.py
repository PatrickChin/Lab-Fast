import os
import numpy as np
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

        self.label_value = QtWidgets.QLabel("Value", parent=self)
        self.label_value.setIndent(22)
        self.layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_value)

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

    def set_values(self, x1, x2, val, std):
        self.start.setValue(x1)
        self.end.setValue(x2)
        self.value.setValue(val)
        self.std.setValue(std)

def calc_radiated_power(temp, surface_area=0.0010187, emissivity=0.04):
    return surface_area * emissivity * const.Stefan_Boltzmann * (temp**4)

def calc_thermal_conductivity(power, iv, temp_diff, surface_area=5.655e-7, length=0.01):
    return np.abs(length*(iv-power)/(surface_area*temp_diff))

def calc_thermal_conductivity2(power, current, voltage, temp_diff, surface_area=5.655e-7, length=0.01):
    return np.abs(length*(current*voltage-power)/(surface_area*temp_diff))


class LowTempCalData:

    dtype = np.dtype([('time',np.int), ('current',np.float),
        ('voltage',np.float), ('temperature',np.float)])

    def __init__(self, filename, voltage=0, dt=1.0):
        self.voltage = voltage
        self.dt = dt

        self.tmin_x1 = 1
        self.tmin_x2 = 1
        self.tmin_val = 1
        self.tmin_std = 1

        self.tmax_x1 = 1
        self.tmax_x2 = 1
        self.tmax_val = 1
        self.tmax_std = 1

        self.cv_x1 = 1
        self.cv_x2 = 1
        self.cv_val = 1
        self.cv_std = 1

        self.kt_x1 = 1
        self.kt_x2 = 1
        self.kt_val = 1
        self.kt_std = 1

        self.data = np.loadtxt(filename, delimiter=',', dtype=LowTempCalData.dtype)[::-1]
        self.line = Line2D(self.data['time'], self.data['temperature'], label=os.path.basename(filename), visible=False)


class LowTempCalApp(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(LowTempCalApp, self).__init__()
        self.setupUi(self)

        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylim(70,140)
        self.ax.set_xlim(0,14000)
        self.canvas = FigureCanvas(self.fig)
        self.graph_layout.addWidget(self.canvas)
        self.canvas.draw()

        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.graph_layout.addWidget(self.toolbar)
 
        self.prev_dir = '.'
        self.file_import_button.clicked.connect(self.import_dialog)
        self.filenames = []
        self.data = []
        self.cur_index = 0

        self.file_list_box.currentIndexChanged.connect(self.file_change)

        self.tmax_group = LowTempCalValueGroup("Max Temperature", self.value_layout)
        self.value_layout.setWidget(self.value_layout.count(), QtWidgets.QFormLayout.SpanningRole, self.tmax_group.radio)
        self.value_layout.setWidget(self.value_layout.count(), QtWidgets.QFormLayout.SpanningRole, self.tmax_group)

        self.tmin_group = LowTempCalValueGroup("Min Temperature", self.value_layout)
        self.value_layout.setWidget(self.value_layout.count(), QtWidgets.QFormLayout.SpanningRole, self.tmin_group.radio)
        self.value_layout.setWidget(self.value_layout.count(), QtWidgets.QFormLayout.SpanningRole, self.tmin_group)

        # self.kt_group = LowTempCalValueGroup("Thermal Conductivity", self.value_layout)
        # self.value_layout.setWidget(self.value_layout.count(), QtWidgets.QFormLayout.SpanningRole, self.kt_group.radio)
        # self.value_layout.setWidget(self.value_layout.count(), QtWidgets.QFormLayout.SpanningRole, self.kt_group)

        self.cv_group = LowTempCalValueGroup("Specific Heat", self.value_layout)
        self.value_layout.setWidget(self.value_layout.count(), QtWidgets.QFormLayout.SpanningRole, self.cv_group.radio)
        self.value_layout.setWidget(self.value_layout.count(), QtWidgets.QFormLayout.SpanningRole, self.cv_group)

        self.tmax_group.radio.toggle()


        self.span = SpanSelector(self.ax, self.on_span_select, 'horizontal', useblit=False,
                span_stays=False, rectprops=dict(alpha=0.2, facecolor='blue') )

    def on_span_select(self, x1, x2):
        d = self.data[self.cur_index]
        x1 = max(0, int(x1/d.dt))
        x2 = min(len(d.data)-1, int(x2/d.dt))
        if self.tmax_group.radio.isChecked():
            val = np.mean(np.array(d.data['temperature'][x1:x2]))
            std = np.std(np.array(d.data['temperature'][x1:x2]))
            self.tmax_group.set_values(x1, x2, val, std)
        elif self.tmin_group.radio.isChecked():
            val = np.mean(np.array(d.data['temperature'][x1:x2]))
            std = np.std(np.array(d.data['temperature'][x1:x2]))
            self.tmin_group.set_values(x1, x2, val, std)

        elif self.cv_group.radio.isChecked():
            val = np.mean(np.array(d.data['temperature'][x1:x2]))
            std = np.std(np.array(d.data['temperature'][x1:x2]))
            self.cv_group.set_values(x1, x2, val, std)

    def file_change(self, index):
        self.cur_index = index
        if len(self.data) < 1:
            return

        for i, d in enumerate(self.data):
            d.line.set_visible(i == index)
            # self.ax.lines[i].set_visible(i == index)
        self.ax.relim(True)
        self.ax.autoscale()
        self.canvas.draw()

        d = self.data[index]
        self.tmax_group.set_values(d.tmax_x1, d.tmax_x2, d.tmax_val, d.tmax_std)
        self.tmin_group.set_values(d.tmin_x1, d.tmin_x2, d.tmin_val, d.tmin_std)
        self.cv_group.set_values(d.cv_x1, d.cv_x2, d.cv_val, d.cv_std)
        # self.kt_group.set_values(d.kt_x1, d.kt_x2, d.kt_val, d.kt_std)

        ld = len(d.data)
        self.tmax_group.start.setMaximum(ld)
        self.tmin_group.start.setMaximum(ld)
        self.cv_group.start.setMaximum(ld)
        # self.kt_group.start.setMaximum(ld)
        self.tmax_group.end.setMaximum(ld)
        self.tmin_group.end.setMaximum(ld)
        self.cv_group.end.setMaximum(ld)
        # self.kt_group.end.setMaximum(ld)

    def import_dialog(self):
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
                self, 'Select one or more data files to import', directory=self.prev_dir)
        if len(filenames) < 1:
            return
        self.import_files(filenames)

    def import_files(self, filenames):
        for f in filenames:
            if f in self.filenames:
                print('Not importing \"{}\", it was already imported'.format(f))
                continue
            self.filenames.append(f)
            self.file_list_box.addItem(os.path.basename(f))
            item = LowTempCalData(f)
            self.data.append(item)
            self.ax.add_line(item.line)
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

