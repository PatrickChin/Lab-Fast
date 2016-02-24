import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUiType
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from lowtempcal import LowTempCalItem

Ui_MainWindow, QMainWindow = loadUiType('mainwindow.ui')

class Main(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)

        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.graph_layout.addWidget(self.canvas)
        self.canvas.draw()
 
        self.prev_dir = '.'
        self.file_import_button.clicked.connect(self.importButton)
        self.files = []

    def importButton(self):
        filenames = QtWidgets.QFileDialog.getOpenFileNames(
                self, 'Select one or more data files to import', directory=self.prev_dir)
        self.prev_dir = os.path.dirname(filenames[0][0])
        for f in filenames[0]: # unsure why this is an array of array
            if f in self.files:
                print('Not importing \"{}\", it was already imported'.format(f))
                break
            self.files.append(f)
            cur_item = LowTempCalItem.from_file(f, self.file_list)
            self.file_list.addItem(cur_item)
            self.ax.plot(cur_item.data['time'], cur_item.data['temperature'])
            self.canvas.draw()

if __name__ == '__main__':
    import sys
 
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())
