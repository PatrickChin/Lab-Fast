from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUiType
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

Ui_MainWindow, QMainWindow = loadUiType('mainwindow.ui')

class Main(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)

        self.file_import_button.clicked.connect(self.importButton)

    def importButton(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self)
        self.file_list.addItem(filename)

    def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.graph_layout.addWidget(self.canvas)
        self.canvas.draw()
 
if __name__ == '__main__':
    import sys
    import numpy as np
 
    fig1 = Figure()
    ax1 = fig1.add_subplot(111)
 
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.addmpl(fig1)
    main.show()
    sys.exit(app.exec_())
