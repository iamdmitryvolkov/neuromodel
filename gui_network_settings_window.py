# gui 2.0 window
# 30.09.2015 Dmitry Volkov

# QT5
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QTabWidget, QMessageBox, QWidget
from PyQt5.QtGui import QIntValidator, QPainter, QColor, QBrush

# GUI
from gui_consts import *

# window class
class NetworkSettingsWindow(QWidget):
    # parent
    __parent = None

    # Initialization
    def __init__(self, parent):
        super().__init__()

        self.__parent = parent
        parent.setEnabled(False)
        parent.worker.pause()

        uic.loadUi('GUI/forms/network_settings_form.ui', self)
        self.init_ui()

        self.show()

    # Window UI
    def init_ui(self):
        pass

    # override
    def closeEvent(self, event):
        self.__parent.setEnabled(True)

    # Message Box
    def message_box(self, text, title=MESSAGE_TEXT):
        QMessageBox.question(self, title, text, QMessageBox.Ok)
