# gui 2.0 window
# 30.09.2015 Dmitry Volkov

# QT5
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QWidget

# GUI
from gui_network_worker import *
from gui_neuron_parameters_window import *
from gui_network_settings_window import *
from gui_settings_window import *

# network
from network import *

# util
from fs_worker import *


# window class
class NetworkWindow(QWidget):
    # network
    ntw = None

    # worker
    worker = None

    # child
    child = None

    # buffer
    __buffer = 0
    __buffer_data = ""
    __current_buffer_len = 0

    # Initialization
    def __init__(self):
        super().__init__()

        uic.loadUi('GUI/forms/main_form.ui', self)
        self.init_ui()

        self.worker = NetworkWorker(self)

        # load matrix
        load = load_parameter(KEY_SETTINGS_TAB, DEFAULT_SETTINGS_TAB) == "1"
        if load:
            load_type = int(load_parameter(KEY_LOAD_NETWORK_COMBOBOX, DEFAULT_LOAD_NETWORK_COMBOBOX))
            if load_type == 0:
                if self.load_save(LASTSAVE_FILEPATH):
                    print("Last network restored")
                else:
                    print("Error loading last network")
                    self.create_new_network()
            elif(load_type == 1):
                if self.load_save(SAVES_FILEPATH + "/" + load_parameter(KEY_SAVED_FILE, DEFAULT_SAVED_FILE)):
                    print("Network loaded")
                else:
                    print("Error loading network")
                    self.create_new_network()
            elif(load_type == 2):
                self.ntw = Network(1, 1, 0, 0, parentGui=self.worker)
                m = load_matrix(load_parameter(KEY_ELECTRODES_MATRIX_PATH, DEFAULT_ELECTRODES_MATRIX_PATH))
                if (not m is None):
                    self.ntw.ele_matrix_put(m)
                    print("Electrodes matrix successfully loaded")
                m = load_matrix(load_parameter(KEY_NEURONS_MATRIX_PATH, DEFAULT_NEURONS_MATRIX_PATH))
                if (not m is None):
                    self.ntw.neu_matrix_put(m)
                    print("Neurons matrix successfully loaded")
                self.ntw.setNoize(DEFAULT_NOIZE_TYPE, DEFAULT_NOIZE_VAL)
        else:
            self.create_new_network()

        buf = 0
        if load_parameter(KEY_BUFFERED_OUTPUT_VALUE, DEFAULT_BUFFERED_OUTPUT_VALUE) == "True":
            buf = int(load_parameter(KEY_BUFFERED_OUTPUT_VALUE, DEFAULT_BUFFERED_OUTPUT_VALUE))
        self.set_buffer(buf)

        if self.ntw.getNoize()[0]:
            self.NoizeTypeComboBox.setCurrentIndex(0)
            self.NoizeValueSpinBox.setMaximum(100)
            self.NoizeValueSpinBox.setValue(self.ntw.getNoize()[1])
        else:
            self.NoizeTypeComboBox.setCurrentIndex(1)
            self.NoizeValueSpinBox.setMaximum(self.ntw.getNeuronsCount())
            self.NoizeValueSpinBox.setValue(self.ntw.getNoize()[1])

        self.worker.set_save_to_file(True)

        self.show()

    # Window UI
    def init_ui(self):
        self.StartStopButton.clicked.connect(self.sub_start_pause)
        self.NeuronParametersButton.clicked.connect(self.sub_neuron_params)
        self.NetworkButton.clicked.connect(self.sub_network_settings)
        self.NetworkButton.setEnabled(False)
        self.SettingsButton.clicked.connect(self.sub_app_settings)
        self.NoizeTypeComboBox.currentIndexChanged.connect(self.sub_select_noize_type)
        self.NoizeValueSpinBox.valueChanged.connect(self.sub_select_noize_value)

    def create_new_network(self):
        neurs = int(load_parameter(KEY_NEURONS_COUNT, DEFAULT_NEURONS_COUNT))
        elects = int(load_parameter(KEY_ELECTRODES_COUNT, DEFAULT_ELECTRODES_COUNT))
        neurs_con = int(load_parameter(KEY_NEURONS_CONNECTIONS, DEFAULT_NEURONS_CONNECTIONS))
        elects_con = int(load_parameter(KEY_ELECTRODES_CONNECTIONS, DEFAULT_ELECTRODES_CONNECTIONS))
        self.ntw = Network(1, 1, 0, 0, parentGui=self.worker)
        for i in range(neurs - 1):
            self.ntw.addNeurons(1, 0, 0, 0, 0)
        for i in range(elects - 1):
            self.ntw.addElectrodes(1, 0, 0, 0)
        self.ntw.addConnections(True, neurs_con, 0, neurs - 1, 0, neurs - 1)
        self.ntw.addConnections(False, elects_con, 0, neurs - 1, 0, elects - 1)
        self.ntw.setNoize(DEFAULT_NOIZE_TYPE, DEFAULT_NOIZE_VAL)
        print("New network created")

    def load_save(self, file):
        print("not supported yet")
        return False

    # override
    def closeEvent(self, event):
        if self.worker is not None:
            self.worker.end_worker()
            self.worker.join()
        if self.child is not None:
            self.child.close()
            self.child = None
        # TODO: save last network

    # Message Box
    def message_box(self, text, title=MESSAGE_TEXT):
        QMessageBox.question(self, title, text, QMessageBox.Ok)

    # buffer size
    def set_buffer(self, val):
        self.__buffer = val

    # clear buffer
    def print_now(self):
        if self.__buffer_data != "":
            print(self.__buffer_data)
            self.__buffer_data = ""
        self.__current_buffer_len = 0

    # Buffered printer
    def print_data(self, data):
        addon = ""
        if self.__current_buffer_len > 0:
            addon = "\n"
        self.__buffer_data = self.__buffer_data + addon + data
        self.__current_buffer_len += 1
        if self.__buffer <= self.__current_buffer_len:
            self.print_now()


    # subs methods
    def sub_start_pause(self):
        self.worker.flip_running()

    def sub_neuron_params(self):
        self.child = ParametersWindow(self)

    def sub_network_settings(self):
        self.NeuronParametersButton.setEnabled(True)
        self.worker.suspend()
        self.child = NetworkSettingsWindow(self)

    def sub_app_settings(self):
        self.NeuronParametersButton.setEnabled(True)
        self.worker.suspend()
        self.child = SettingsWindow(self)

    def sub_select_noize_type(self, index):
        neurs = self.ntw.getNeuronsCount()
        old_noize = self.ntw.getNoize()
        if old_noize[0] != (not index):
            if not index:  # relative
                self.NoizeValueSpinBox.setMaximum(100)
                self.NoizeValueSpinBox.setValue(int(old_noize[1] * 100 / neurs))
            else:
                self.NoizeValueSpinBox.setMaximum(neurs)
                self.NoizeValueSpinBox.setValue(min(int(old_noize[1] * 100), neurs))
        self.ntw.setNoize(not index, self.NoizeValueSpinBox.value())

    def sub_select_noize_value(self, value):
        self.ntw.setNoize(not self.NoizeTypeComboBox.currentIndex(), value)

