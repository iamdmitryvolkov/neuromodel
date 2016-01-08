# gui 2.0 window
# 30.09.2015 Dmitry Volkov

# QT5
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QWidget

# GUI


from os.path import isfile
from shared_libs import fs_worker as fs
from GUI.gui_settings_default_parameters import *
from GUI.gui_settings_keys import *
from GUI.gui_consts import *

# window class
class SettingsWindow(QWidget):
    # parent
    __parent = None

    __restore_state_flag_lock = False
    __restore_state_flag = False

    __savedFiles = []

    # Initialization
    def __init__(self, parent):
        super().__init__()

        self.__parent = parent
        parent.setEnabled(False)
        parent.worker.pause()

        uic.loadUi('GUI/forms/settings_form.ui', self)
        self.init_ui()

        # buffer
        self.BufferGroupBox.setChecked("True" == fs.load_parameter(KEY_BUFFERED_OUTPUT_FLAG, DEFAULT_BUFFERED_OUTPUT_FLAG))
        self.BufferValue.setValue(int(fs.load_parameter(KEY_BUFFERED_OUTPUT_VALUE, DEFAULT_BUFFERED_OUTPUT_VALUE)))

        self.StartupTabs.setCurrentIndex(int(fs.load_parameter(KEY_SETTINGS_TAB, DEFAULT_SETTINGS_TAB)))

        # 1 page
        self.NeuronsCountBox.setValue(int(fs.load_parameter(KEY_NEURONS_COUNT, DEFAULT_NEURONS_COUNT)))
        self.ElectrodesCountBox.setValue(int(fs.load_parameter(KEY_ELECTRODES_COUNT, DEFAULT_ELECTRODES_COUNT)))
        self.ElectrodesConnectionsBox.setValue(int(fs.load_parameter(KEY_ELECTRODES_CONNECTIONS, DEFAULT_ELECTRODES_CONNECTIONS)))
        self.NeuronsConnectionsBox.setValue(int(fs.load_parameter(KEY_NEURONS_CONNECTIONS, DEFAULT_NEURONS_CONNECTIONS)))

        # 2 page

        self.LoadTypeComboBox.setCurrentIndex(int(fs.load_parameter(KEY_LOAD_NETWORK_COMBOBOX, DEFAULT_LOAD_NETWORK_COMBOBOX)));
        self.__restore_state_flag = "True" == fs.load_parameter(KEY_RESTORE_STATE_FLAG, DEFAULT_RESTORE_STATE_FLAG)
        self.RestoreStateCheckBox.setChecked(self.__restore_state_flag)
        self.__savedFiles = get_saved_files()
        self.SelectSavedFileComboBox.addItems(self.__savedFiles)
        saved_file = fs.load_parameter(KEY_SAVED_FILE,DEFAULT_SAVED_FILE)
        for i in range(len(self.__savedFiles)):
            if self.__savedFiles[i] == saved_file:
                self.SelectSavedFileComboBox.setCurrentIndex(i+1)
                break;

        self.sub_load_type_combobox(self.LoadTypeComboBox.currentIndex())

        self.ElectrodesMatrixLineEdit.setText(fs.load_parameter(KEY_ELECTRODES_MATRIX_PATH, DEFAULT_ELECTRODES_MATRIX_PATH))
        self.NeuronsMatrixLineEdit.setText(fs.load_parameter(KEY_NEURONS_MATRIX_PATH, DEFAULT_NEURONS_MATRIX_PATH))
        self.show()

    # Window UI
    def init_ui(self):
        self.ResetButton.clicked.connect(self.sub_restore_click)
        self.SaveButton.clicked.connect(self.sub_save_click)
        self.StartupTabs.currentChanged.connect(self.sub_select_tab)
        self.NeuronsCountBox.valueChanged.connect(self.sub_new_neu_ele_value)
        self.ElectrodesCountBox.valueChanged.connect(self.sub_new_neu_ele_value)
        self.LoadTypeComboBox.currentIndexChanged.connect(self.sub_load_type_combobox)
        self.RestoreStateCheckBox.stateChanged.connect(self.sub_restore_state_check_box)
        self.SelectSavedFileComboBox.currentIndexChanged.connect(self.sub_saved_file_selected)
        self.ElectrodesMatrixLineEdit.textChanged.connect(self.check_matrix_file_path)
        self.NeuronsMatrixLineEdit.textChanged.connect(self.check_matrix_file_path)
        self.PathButton.clicked.connect(self.sub_select_path)


    # override
    def closeEvent(self, event):
        self.__parent.setEnabled(True)
        self.__parent.worker.resume()

    # Message Box
    def message_box(self, text, title=MESSAGE_TEXT):
        QMessageBox.question(self, title, text, QMessageBox.Ok)

    def check_matrix_file_path(self):
        f1 = isfile(self.ElectrodesMatrixLineEdit.displayText())
        f2 = isfile(self.NeuronsMatrixLineEdit.displayText())
        self.SaveButton.setEnabled(f1 and f2)
        if f1:
            self.ElectrodesMatrixLineEdit.setStyleSheet(SETTINGS_COLOR_OK)
        else:
            self.ElectrodesMatrixLineEdit.setStyleSheet(SETTINGS_COLOR_BAD)
        if f2:
            self.NeuronsMatrixLineEdit.setStyleSheet(SETTINGS_COLOR_OK)
        else:
            self.NeuronsMatrixLineEdit.setStyleSheet(SETTINGS_COLOR_BAD)


    # subs

    def sub_restore_click(self):
        clear_settings()
        self.close()

    def sub_save_click(self):
        fs.fs.save_parameter(KEY_BUFFERED_OUTPUT_FLAG, self.BufferGroupBox.isChecked())
        fs.fs.save_parameter(KEY_BUFFERED_OUTPUT_VALUE, self.BufferValue.value())

        fs.fs.save_parameter(KEY_SETTINGS_TAB, self.StartupTabs.currentIndex())

        fs.fs.save_parameter(KEY_NEURONS_COUNT, self.NeuronsCountBox.value())
        fs.fs.save_parameter(KEY_ELECTRODES_COUNT, self.ElectrodesCountBox.value())
        fs.fs.save_parameter(KEY_ELECTRODES_CONNECTIONS, self.ElectrodesConnectionsBox.value())
        fs.fs.save_parameter(KEY_NEURONS_CONNECTIONS, self.NeuronsConnectionsBox.value())

        fs.fs.save_parameter(KEY_LOAD_NETWORK_COMBOBOX, self.LoadTypeComboBox.currentIndex())
        fs.fs.save_parameter(KEY_RESTORE_STATE_FLAG, self.__restore_state_flag)
        if len(self.__savedFiles) > 0 and self.SelectSavedFileComboBox.currentIndex() > 0:
            fs.fs.save_parameter(KEY_SAVED_FILE, self.__savedFiles[self.SelectSavedFileComboBox.currentIndex() - 1])
        fs.fs.save_parameter(KEY_ELECTRODES_MATRIX_PATH, self.ElectrodesMatrixLineEdit.displayText())
        fs.fs.save_parameter(KEY_NEURONS_MATRIX_PATH, self.NeuronsMatrixLineEdit.displayText())
        if self.BufferGroupBox.isChecked():
            self.__parent.set_buffer(self.BufferValue.value())
        else:
            self.__parent.set_buffer(0)
        self.close()

    def sub_select_tab(self, index):
        if ((index) and (self.LoadTypeComboBox.currentIndex() == 1) and (self.SelectSavedFileComboBox.currentIndex() == 0)):
            self.SaveButton.setEnabled(False)
        else:
            self.SaveButton.setEnabled(True)
        if ((index) and (self.LoadTypeComboBox.currentIndex() == 2)):
            self.check_matrix_file_path()

    def sub_new_neu_ele_value(self, value):
        vneu = self.NeuronsCountBox.value()
        vele = self.ElectrodesCountBox.value()
        self.ElectrodesConnectionsBox.setMaximum(vneu*vele)
        self.NeuronsConnectionsBox.setMaximum(vneu*vneu)

    def sub_load_type_combobox(self, index):
        if index == 0:
            self.SelectSavedFileComboBox.setEnabled(False)
            self.ElectrodesMatrixLineEdit.setEnabled(False)
            self.NeuronsMatrixLineEdit.setEnabled(False)
            self.RestoreStateCheckBox.setEnabled(True)
            self.RestoreStateCheckBox.setChecked(self.__restore_state_flag)
            self.PathButton.setEnabled(False)
            self.SaveButton.setEnabled(True)
            self.ElectrodesMatrixLineEdit.setStyleSheet(SETTINGS_COLOR_NEUTRAL)
            self.NeuronsMatrixLineEdit.setStyleSheet(SETTINGS_COLOR_NEUTRAL)
        elif index == 1:
            self.SelectSavedFileComboBox.setEnabled(True)
            self.ElectrodesMatrixLineEdit.setEnabled(False)
            self.NeuronsMatrixLineEdit.setEnabled(False)
            self.RestoreStateCheckBox.setEnabled(True)
            self.RestoreStateCheckBox.setChecked(self.__restore_state_flag)
            self.PathButton.setEnabled(False)
            if self.SelectSavedFileComboBox.currentIndex() == 0:
                self.SaveButton.setEnabled(False)
            else:
                self.SaveButton.setEnabled(True)
            self.ElectrodesMatrixLineEdit.setStyleSheet(SETTINGS_COLOR_NEUTRAL)
            self.NeuronsMatrixLineEdit.setStyleSheet(SETTINGS_COLOR_NEUTRAL)
        elif index == 2:
            self.SelectSavedFileComboBox.setEnabled(False)
            self.ElectrodesMatrixLineEdit.setEnabled(True)
            self.NeuronsMatrixLineEdit.setEnabled(True)
            self.RestoreStateCheckBox.setEnabled(False)
            self.__restore_state_flag_lock = True
            self.RestoreStateCheckBox.setChecked(False)
            self.__restore_state_flag_lock = False
            self.PathButton.setEnabled(True)
            self.check_matrix_file_path()

    def sub_saved_file_selected(self, file):
        self.SaveButton.setEnabled(file > 0)

    def sub_restore_state_check_box(self, state):
        if not self.__restore_state_flag_lock:
            self.__restore_state_flag = bool(state)

    def sub_select_path(self, file):
        neu = QtWidgets.QFileDialog.getOpenFileName(self, DIALOG_NEU_TEXT, DIALOG_STARTUP_PATH)[0]
        ele = QtWidgets.QFileDialog.getOpenFileName(self, DIALOG_ELE_TEXT, DIALOG_STARTUP_PATH)[0]
        if neu != "":
            self.NeuronsMatrixLineEdit.setText(neu)
        if ele != "":
            self.ElectrodesMatrixLineEdit.setText(ele)

