#!/usr/bin/env python

from PyQt5 import QtCore, QtWidgets
from lowtempcal.gui import LowTempCalApp


if __name__ == '__main__':
    import sys
 
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyle("breeze")

    app_window = LowTempCalApp()
    # app_window.import_files([
    #     './binary_data/2V',
    #     './binary_data/3V',
    #     './binary_data/4V',
    #     './binary_data/5V'
    # ], binary=True)
    # app_window.file_change(0)

    app_window.show()
    sys.exit(app.exec_())
