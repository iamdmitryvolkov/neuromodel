# gui 2.0 window
# 30.09.2015 Dmitry Volkov

# QT5
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QTabWidget, QMessageBox, QWidget
from PyQt5.QtGui import QIntValidator, QPainter, QColor, QBrush

# GUI
from gui_consts import *

from fs_worker import *
from gui_settings_default_parameters import *
from gui_settings_keys import *

# window class
class SettingsWindow(QWidget):
    # parent
    __parent = None

    __restore_state_flag_lock = False
    __restore_state_flag = False

    # Initialization
    def __init__(self, parent):
        super().__init__()

        self.__parent = parent
        parent.setEnabled(False)
        parent.worker.pause()

        uic.loadUi('GUI/forms/settings_form.ui', self)
        self.init_ui()

        # buffer


        self.StartupTabs.setCurrentIndex(DEFAULT_SETTINGS_TAB)

        # 1 page
        self.NeuronsCountBox.setValue(int(loadParameter(KEY_NEURONS_COUNT, DEFAULT_NEURONS_COUNT)))
        self.ElectrodesCountBox.setValue(int(loadParameter(KEY_ELECTRODES_COUNT, DEFAULT_ELECTRODES_COUNT)))
        self.ElectrodesConnectionsBox.setValue(int(loadParameter(KEY_ELECTRODES_CONNECTIONS, DEFAULT_ELECTRODES_CONNECTIONS)))
        self.NeuronsConnectionsBox.setValue(int(loadParameter(KEY_NEURONS_CONNECTIONS, DEFAULT_NEURONS_CONNECTIONS)))

        # 2 page

        self.LoadTypeComboBox.setCurrentIndex(int(loadParameter(KEY_LOAD_NETWORK_COMBOBOX, DEFAULT_LOAD_NETWORK_COMBOBOX)));
        self.__restore_state_flag = bool(loadParameter(KEY_RESTORE_STATE_FLAG, DEFAULT_RESTORE_STATE_FLAG))
        self.RestoreStateCheckBox.setChecked(self.__restore_state_flag)

        self.sub_load_type_combobox(self.LoadTypeComboBox.currentIndex())
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
        #self.SelectSavedFileComboBox
        #self.ElectrodesMatrixLineEdit
        #self.NeuronsMatrixLineEdit

        #self.PathButton
        #self.BufferGroupBox
        #self.BufferValue


    # override
    def closeEvent(self, event):
        self.__parent.setEnabled(True)
        self.__parent.worker.resume()

    # Message Box
    def message_box(self, text, title=MESSAGE_TEXT):
        QMessageBox.question(self, title, text, QMessageBox.Ok)

    # subs

    def sub_restore_click(self):
        clearSettings()
        self.close()

    def sub_save_click(self):
        print("not supported yet")
        self.close()

    def sub_select_tab(self, index):
        if ((index) and (self.LoadTypeComboBox.currentIndex() == 1) and (self.SelectSavedFileComboBox.currentIndex() == 0)):
            self.SaveButton.setEnabled(False)
        else:
            self.SaveButton.setEnabled(True)

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
        elif index == 2:
            self.SelectSavedFileComboBox.setEnabled(False)
            self.ElectrodesMatrixLineEdit.setEnabled(True)
            self.NeuronsMatrixLineEdit.setEnabled(True)
            self.RestoreStateCheckBox.setEnabled(False)
            self.__restore_state_flag_lock = True
            self.RestoreStateCheckBox.setChecked(False)
            self.__restore_state_flag_lock = False
            self.PathButton.setEnabled(True)
            self.SaveButton.setEnabled(True)

    def sub_saved_file_selected(self, file):
        print(file)

    def sub_restore_state_check_box(self, state):
        if not self.__restore_state_flag_lock:
            self.__restore_state_flag = bool(state)