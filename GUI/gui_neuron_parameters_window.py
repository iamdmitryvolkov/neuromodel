# gui 2.0 window
# 30.09.2015 Dmitry Volkov

# QT5
from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QWidget

# GUI
from GUI.gui_consts import *
from model.params_consts import *


# window class
class ParametersWindow(QWidget):
    # network
    __network = None

    # parent
    __parent = None

    __parameters_set = []

    # Initialization
    def __init__(self, parent):
        super().__init__()

        self.__network = parent.ntw
        parent.NeuronParametersButton.setEnabled(False)
        self.__parent = parent

        uic.loadUi('GUI/forms/neuron_parameters_form.ui', self)
        self.init_ui()

        # load parameters from network
        self.ElectrodeSensitivitySlider.setValue(self.__network.get_parameter(ID_SENSITIVITY)*10)
        self.ThresholdSpinBox.setValue(self.__network.get_parameter(ID_THRESHOLD))
        self.PotentialRelaxTimeSpinBox.setValue(self.__network.get_parameter(ID_POTENTIAL_RELAX_TIME))
        self.StrengthMinSpinBox.setValue(self.__network.get_parameter(ID_STRENGTH_MIN))
        self.StrengthMaxSpinBox.setValue(self.__network.get_parameter(ID_STRENGTH_MAX))
        self.StrengthRelaxTimeSpinBox.setValue(self.__network.get_parameter(ID_STRENGTH_RELAX_TIME))
        self.MaxResourceSpinBox.setValue(self.__network.get_parameter(ID_RESOURCE_MAX_BY_STRENGTH))
        self.ResistanceSpinBox.setValue(self.__network.get_parameter(ID_RESISTANCE))
        self.SynMaxSpinBox.setValue(self.__network.get_parameter(ID_SYN_VALUE_MAX))
        self.SynMinSpinBox.setValue(self.__network.get_parameter(ID_SYN_VALUE_MIN))
        self.SynRelaxTimeSpinBox.setValue(self.__network.get_parameter(ID_CONNECTION_RELAX_TIME))
        # self.StimCurrentSpinBox.setValue(self.__network.get_parameter(INJECTOR_ID_RESOURCE_MAX)) # TODO: not working yet

        for i in range(11):
            self.__parameters_set.append(None)

        self.show()

    # Window UI
    def init_ui(self):
        self.RealTimeApplyParametersCheckBox.setChecked(True)
        self.RealTimeApplyParametersCheckBox.stateChanged.connect(self.sub_realtime_checkbox_state)
        self.ApplyNowButton.setEnabled(False)
        self.ApplyNowButton.clicked.connect(self.sub_applynow_button)
        self.ElectrodeSensitivitySlider.valueChanged.connect(self.sub_electrode_sensitivity_slider_move)
        self.ThresholdSpinBox.valueChanged.connect(self.sub_threshold_value)
        self.PotentialRelaxTimeSpinBox.valueChanged.connect(self.sub_potential_relax_time_value)
        self.StrengthMinSpinBox.valueChanged.connect(self.sub_strength_min)
        self.StrengthMaxSpinBox.valueChanged.connect(self.sub_strength_max)
        self.StrengthRelaxTimeSpinBox.valueChanged.connect(self.sub_strength_relax_time)
        self.MaxResourceSpinBox.valueChanged.connect(self.sub_max_resource)
        self.ResistanceSpinBox.valueChanged.connect(self.sub_resistance)
        self.SynMaxSpinBox.valueChanged.connect(self.sub_syn_max)
        self.SynMinSpinBox.valueChanged.connect(self.sub_syn_min)
        self.SynRelaxTimeSpinBox.valueChanged.connect(self.sub_syn_relax_time)
        self.StimCurrentSpinBox.valueChanged.connect(self.sub_stim_current)
        self.StimCurrentSpinBox.setEnabled(False)  # TODO : not working yet

    # override
    def closeEvent(self, event):
        self.__parent.NeuronParametersButton.setEnabled(True)

    # Message Box
    def message_box(self, text, title=MESSAGE_TEXT):
        QMessageBox.question(self, title, text, QMessageBox.Ok)

    # apply parameter
    def push(self, injector_id, value):
        self.__network.set_parameter(injector_id, value)

    #subs
    def sub_realtime_checkbox_state(self, state):
        self.ApplyNowButton.setEnabled(not state)
        self.sub_applynow_button()

    def sub_applynow_button(self):
        self.__parent.worker.suspend()
        self.__parent.worker.join()
        for i in range(len(self.__parameters_set)):
            if not self.__parameters_set[i] is None:
                self.push(i, self.__parameters_set[i])
                self.__parameters_set[i] = None
        self.__parent.worker.resume()

    def sub_electrode_sensitivity_slider_move(self, value):
        self.ElectrodeSensitivityLabel.setText("Electrode sensitivity: " + str(value/10))
        inj_const = ID_SENSITIVITY
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, (value/10))
        else:
            self.__parameters_set[inj_const] = (value/10)

    def sub_threshold_value(self, value):
        inj_const = ID_THRESHOLD
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_potential_relax_time_value(self, value):
        inj_const = ID_POTENTIAL_RELAX_TIME
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_strength_min(self, value):
        inj_const = ID_STRENGTH_MIN
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_strength_max(self, value):
        inj_const = ID_STRENGTH_MAX
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_strength_relax_time(self, value):
        inj_const = ID_STRENGTH_RELAX_TIME
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_max_resource(self, value):
        inj_const = ID_RESOURCE_MAX_BY_STRENGTH
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_resistance(self, value):
        inj_const = ID_RESISTANCE
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_syn_max(self, value):
        inj_const = ID_SYN_VALUE_MAX
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_syn_min(self, value):
        inj_const = ID_SYN_VALUE_MIN
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_syn_relax_time(self, value):
        inj_const = ID_CONNECTION_RELAX_TIME
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_stim_current(self, value):
        # TODO: not working yet
        inj_const = 11
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value


