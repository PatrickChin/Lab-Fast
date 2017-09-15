import os
import numpy as np
import matplotlib as mpl
import scipy.stats as stats

# Test for the PyQt5 library, if this fails import PyQt4
try:
    from PyQt5 import QtCore, QtWidgets
    from PyQt5.uic import loadUiType
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvasQTAgg as FigureCanvas,
        NavigationToolbar2QT as NavigationToolbar)
    mpl.use('Qt5Agg')
    qt5 = True
except ImportError:
    from PyQt4 import QtCore
    from PyQt4 import QtGui as QtWidgets
    from PyQt4.uic import loadUiType
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvasQTAgg as FigureCanvas,
        NavigationToolbar2QT as NavigationToolbar)
    mpl.use('Qt4Agg')
    qt5 = False

from matplotlib.lines import Line2D
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector


class LowTempCalValueGroup(QtWidgets.QWidget):

    def __init__(self, text, parent):
        super(QtWidgets.QWidget, self).__init__()

        # Add form layout to widget
        self.layout = QtWidgets.QFormLayout(self)

        # Radio button is added to parent
        self.radio = QtWidgets.QRadioButton(text)
        self.radio.toggled.connect(self.setEnabled)
        parent.addWidget(self.radio)

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
        self.value.setMaximum(99999.0)
        self.value.setReadOnly(True)
        self.value.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.value)

        self.label_std = QtWidgets.QLabel("Std", parent=self)
        self.label_std.setIndent(22)
        self.layout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_std)
        self.std = QtWidgets.QDoubleSpinBox(self)
        self.std.setMaximum(99999.0)
        self.std.setReadOnly(True)
        self.std.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.layout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.std)

        self.setEnabled(False)

        parent.addWidget(self, parent.rowCount(), 0, 1, 2)


    def set_values(self, x1, x2, val, std):
        self.start.setValue(x1)
        self.end.setValue(x2)
        self.value.setValue(val)
        self.std.setValue(std)



Ui_MainWindow, QMainWindow = loadUiType('mainwindow.ui')
class LowTempCalApp(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(QtWidgets.QMainWindow, self).__init__()
        self.setupUi(self)

        self.fig = Figure(facecolor="white")
        self.ax_current = self.fig.add_subplot(111, frameon=False)
        self.ax_temp = self.ax_current.twinx()
        self.ax_current.yaxis.tick_right()
        self.ax_temp.yaxis.tick_left()
        self.canvas = FigureCanvas(self.fig)
        self.graph_layout.addWidget(self.canvas)
        self.canvas.draw()

        # Show matplotlib toolbar
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.graph_layout.addWidget(self.toolbar)
 
        self.checkbox_show_current.stateChanged.connect(self.show_current_graph)
        self.button_calc.clicked.connect(self.recalc_kt)

        # Import file button
        self.button_file_import.clicked.connect(self.import_dialog)
        self.filenames = []
        self.data = []
        self.cur_index = 0

        # file selector list
        self.combobox_filelist.currentIndexChanged.connect(self.file_change)

        # Input boxes for tmin and tmax
        self.tmin_group = LowTempCalValueGroup("Min Temperature", self.value_layout)
        self.tmax_group = LowTempCalValueGroup("Max Temperature", self.value_layout)

        spacer_value = QtWidgets.QSpacerItem(20, 40,
                                             QtWidgets.QSizePolicy.Minimum,
                                             QtWidgets.QSizePolicy.Expanding)
        self.value_layout.addItem(spacer_value)

        # select tmin automatically
        self.tmin_group.radio.toggle()

        self.span = SpanSelector(self.ax_temp, self.on_span_select,
                                 'horizontal', useblit=False, span_stays=False,
                                 rectprops=dict(alpha=0.1, facecolor='blue'))

        self.button_next.clicked.connect(self.next_page)
        self.button_prev.clicked.connect(self.prev_page)


    def next_page(self):
        self.pages.setCurrentIndex((self.pages.currentIndex()+1) %
                                   self.pages.count())


    def prev_page(self):
        self.pages.setCurrentIndex((self.pages.currentIndex()-1) %
                                   self.pages.count())

        
    def show_current_graph(self, state):
        self.data[self.cur_index].line_current.set_visible(state)
        self.ax_current.get_yaxis().set_visible(state)
        self.ax_current.relim(True)
        # self.ax_current.autoscale()
        self.canvas.draw()


    def on_span_select(self, x1, x2):
        d = self.data[self.cur_index]

        x1 = max(0, int(x1/d.dt))
        x2 = min(len(d.time)-1, int(x2/d.dt))

        temp = d.temp[x1:x2]
        time = d.time[x1:x2]

        if self.pages.currentIndex() == 0:
            if self.tmax_group.radio.isChecked():
                val = np.mean(temp, dtype=np.float64)
                std = np.std(temp, dtype=np.float64)
                self.tmax_group.set_values(x1, x2, val, std)
                d.tmax_x1 = x1
                d.tmax_x2 = x2
                d.tmax = val
                d.tmax_std = std
            elif self.tmin_group.radio.isChecked():
                val = np.mean(temp, dtype=np.float64)
                std = np.std(temp, dtype=np.float64)
                self.tmin_group.set_values(x1, x2, val, std)
                d.tmin_x1 = x1
                d.tmin_x2 = x2
                d.tmin = val
                d.tmin_std = std
        else:
            slope, intercept, r_value, p_value, std_err = stats.linregress(time, temp)
            self.spinbox_cv2.setValue(slope)
            self.spinbox_cv_pval2.setValue(p_value)
            self.spinbox_cv_rval2.setValue(r_value)
            self.spinbox_cv_std2.setValue(std_err)


    def recalc_kt(self):
        d = self.data[self.cur_index]

        # Only calculate for a temperature change larger than 0.1 degrees
        dtemp = d.tmax - d.tmin 
        if dtemp > 0.1:
            power = calc_radiated_power(d.tmax) # , self.spinbox_area.value())
            current = np.mean(d.current[d.tmax_x1:d.tmax_x2], dtype=np.float64)
            d.voltage = self.spinbox_voltage.value()
            d.kt = calc_thermal_conductivity(power, current, d.voltage, dtemp) #, self.spinbox_area.value(), self.spinbox_len.value())
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
        self.tmax_group.set_values(d.tmax_x1, d.tmax_x2, d.tmax, d.tmax_std)
        self.tmin_group.set_values(d.tmin_x1, d.tmin_x2, d.tmin, d.tmin_std)
        self.spinbox_dt.setValue(d.dt)
        self.spinbox_voltage.setValue(d.voltage)
        self.spinbox_length.setValue(d.length)
        self.spinbox_area.setValue(d.area)
        self.spinbox_power.setValue(d.power)
        self.spinbox_kt.setValue(d.kt)

        ld = len(d.time)
        self.tmax_group.start.setMaximum(ld)
        self.tmin_group.start.setMaximum(ld)
        self.tmax_group.end.setMaximum(ld)
        self.tmin_group.end.setMaximum(ld)


    def import_dialog(self):
        global qt5
        filenames = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select one or more data files to import')
        if qt5:
            filenames = filenames[0] # python3 returns extra information
        if len(filenames) < 1:
            return
        self.import_files(filenames)


    def import_files(self, filenames, binary=False):
        for f in filenames:
            f = os.path.abspath(f)
            if f in self.filenames:
                print('Not importing \"{}\", it was already imported'.format(f))
                continue
            print("Adding \"{}\"".format(f))
            self.filenames.append(f)
            self.combobox_filelist.addItem(os.path.basename(f))
            item = LowTempCalData(f, binary)
            self.data.append(item)
            self.ax_temp.add_line(item.line)
            self.ax_current.add_line(item.line_current)
            self.canvas.draw()

