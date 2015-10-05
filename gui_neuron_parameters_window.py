# gui 2.0 window
# 30.09.2015 Dmitry Volkov

# QT5
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QTabWidget, QMessageBox, QWidget
from PyQt5.QtGui import QIntValidator, QPainter, QColor, QBrush

# GUI
from gui_consts import *

# window class
class ParametersWindow(QWidget):
    # network
    __network = None

    # Initialization
    def __init__(self, network):
        super().__init__()

        self.__network = network

        uic.loadUi('GUI/forms/neuron_parameters_form.ui', self)
        self.init_ui()

        self.show()

    # Window UI
    def init_ui(self):
        pass

    # Message Box
    def message_box(self, text, title=MESSAGE_TEXT):
        QMessageBox.question(self, title, text, QMessageBox.Ok)
