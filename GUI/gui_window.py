# gui 2.0 window
# 30.09.2015 Dmitry Volkov

# QT5

# GUI
from GUI.gui_network_settings_window import *
from GUI.gui_neuron_parameters_window import *
from GUI.gui_settings_window import *

from GUI.gui_network_worker import *
# network
from model.network import *

# util
from shared_libs import fs_worker as fs


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

        # TODO: load settings here
        self.create_new_network()
        buf = 0
        if fs.load_parameter(SETTINGS_FILEPATH, KEY_BUFFERED_OUTPUT_VALUE, DEFAULT_BUFFERED_OUTPUT_VALUE) == "True":
            buf = int(fs.load_parameter(SETTINGS_FILEPATH, KEY_BUFFERED_OUTPUT_VALUE, DEFAULT_BUFFERED_OUTPUT_VALUE))
        self.set_buffer(buf)

        if self.ntw.getNoize()[0]:
            self.NoizeTypeComboBox.setCurrentIndex(0)
            self.NoizeValueSpinBox.setMaximum(100)
            self.NoizeValueSpinBox.setValue(self.ntw.getNoize()[1])
        else:
            self.NoizeTypeComboBox.setCurrentIndex(1)
            self.NoizeValueSpinBox.setMaximum(self.ntw.get_neurons_count())
            self.NoizeValueSpinBox.setValue(self.ntw.getNoize()[1])

        self.worker.set_save_to_file(True)

        self.show()

    # Window UI
    def init_ui(self):
        self.StartStopButton.clicked.connect(self.sub_start_pause)
        self.NeuronParametersButton.clicked.connect(self.sub_neuron_params)
        self.NetworkButton.clicked.connect(self.sub_network_settings)
        self.NetworkButton.setEnabled(False)
        self.NeuronParametersButton.setEnabled(False)
        self.SettingsButton.setEnabled(False)
        self.SettingsButton.clicked.connect(self.sub_app_settings)
        self.NoizeTypeComboBox.currentIndexChanged.connect(self.sub_select_noize_type)
        self.NoizeValueSpinBox.valueChanged.connect(self.sub_select_noize_value)

    def create_new_network(self):
        neurs = int(fs.load_parameter(SETTINGS_FILEPATH, KEY_NEURONS_COUNT, DEFAULT_NEURONS_COUNT))
        elects = int(fs.load_parameter(SETTINGS_FILEPATH, KEY_ELECTRODES_COUNT, DEFAULT_ELECTRODES_COUNT))
        neurs_con = int(fs.load_parameter(SETTINGS_FILEPATH, KEY_NEURONS_CONNECTIONS, DEFAULT_NEURONS_CONNECTIONS))
        elects_con = int(fs.load_parameter(SETTINGS_FILEPATH, KEY_ELECTRODES_CONNECTIONS, DEFAULT_ELECTRODES_CONNECTIONS))
        self.ntw = Network(self.worker)
        self.ntw.add_electrodes(elects)
        self.ntw.add_neurons(neurs)
        self.ntw.add_connections(True, neurs_con, 0, neurs - 1, 0, neurs - 1)
        self.ntw.add_connections(False, elects_con, 0, neurs_con - 1, 0, elects - 1)
        self.ntw.setNoize(True, 5)
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
        neurs = self.ntw.get_neurons_count()
        old_noize = self.ntw.getNoize()
        if old_noize[0] != (not index):
            if not index:  # relative
                self.NoizeValueSpinBox.setMaximum(100)
                self.NoizeValueSpinBox.setValue(int(old_noize[1] * 100 / neurs))
            else:
                self.NoizeValueSpinBox.setMaximum(neurs)
                self.NoizeValueSpinBox.setValue(min(int(old_noize[1] * neurs / 100), neurs))
        self.ntw.setNoize(not index, self.NoizeValueSpinBox.value())

    def sub_select_noize_value(self, value):
        self.ntw.setNoize(not self.NoizeTypeComboBox.currentIndex(), value)

