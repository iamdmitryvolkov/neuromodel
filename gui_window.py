# gui 2.0 window
# 30.09.2015 Dmitry Volkov

# QT5
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QTabWidget, QMessageBox, QWidget
from PyQt5.QtGui import QIntValidator, QPainter, QColor, QBrush

# GUI
from gui_network_worker import *
from gui_neuron_parameters_window import *
from gui_network_settings_window import *
from gui_settings_window import *
from gui_consts import *

# network
from network import *


# window class
class NetworkWindow(QWidget):
    # network
    ntw = None

    # worker
    worker = None

    # Initialization
    def __init__(self):
        super().__init__()

        uic.loadUi('GUI/forms/main_form.ui', self)
        self.init_ui()

        self.worker = NetworkWorker(self)
        self.ntw = Network(electrodes=9, neuronsPerElectrod=9, electrodeEnteres=4, neuronsEnteres=15,
                           parentGui=self.worker)
        if self.ntw.getNoize()[0]:
            self
            self.NoizeTypeComboBox.setCurrentIndex(0)
            self.NoizeValueSpinBox.setMaximum(100)
            self.NoizeValueSpinBox.setValue(self.ntw.getNoize()[1])
        else:
            self.NoizeTypeComboBox.setCurrentIndex(1)
            self.NoizeValueSpinBox.setMaximum(self.ntw.getNeuronsCount())
            self.NoizeValueSpinBox.setValue(self.ntw.getNoize()[1])
        self.show()


    # Window UI
    def init_ui(self):
        self.StartStopButton.clicked.connect(self.sub_start_pause)
        self.NeuronParametersButton.clicked.connect(self.sub_neuron_params)
        self.NetworkButton.clicked.connect(self.sub_network_settings)
        self.SettingsButton.clicked.connect(self.sub_app_settings)
        self.NoizeTypeComboBox.currentIndexChanged.connect(self.sub_select_noize_type)
        self.NoizeValueSpinBox.valueChanged.connect(self.sub_select_noize_value)

    # override
    def closeEvent(self, event):
        self.child = None
        self.worker.end_worker()

    # Message Box
    def message_box(self, text, title=MESSAGE_TEXT):
        QMessageBox.question(self, title, text, QMessageBox.Ok)

    # Buffered printer
    def printData(self, data):
        print(data)

    # subs methods
    def sub_start_pause(self):
        self.worker.flip_running()

    def sub_neuron_params(self):
        self.child = ParametersWindow(self)

    def sub_network_settings(self):
        self.child = NetworkSettingsWindow(self)

    def sub_app_settings(self):
        self.child = SettingsWindow(self)

    def sub_select_noize_type(self, index):
        neurs = self.ntw.getNeuronsCount()
        old_noize = self.ntw.getNoize()
        if old_noize[0] != (not index):
            if not index:  # relative
                self.NoizeValueSpinBox.setMaximum(100)
                self.NoizeValueSpinBox.setValue(int(old_noize[1]*100/neurs))
            else:
                self.NoizeValueSpinBox.setMaximum(neurs)
                self.NoizeValueSpinBox.setValue(min(int(old_noize[1]*100),neurs))
        self.ntw.setNoize(not index, self.NoizeValueSpinBox.value())

    def sub_select_noize_value(self, value):
        self.ntw.setNoize(not self.NoizeTypeComboBox.currentIndex(), value)
