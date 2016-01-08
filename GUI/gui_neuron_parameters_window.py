# gui 2.0 window
# 30.09.2015 Dmitry Volkov

# QT5
from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QWidget

# GUI
from GUI.gui_consts import *

#network

# window class
class ParametersWindow(QWidget):
    # network
    __network = None

    #parent
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
        self.ElectrodeSensitivitySlider.setValue(self.__network.get_parameter(INJECTOR_ID_ELECTRODE_THRESHOLD)*10)
        self.StimCurrentSpinBox.setValue(self.__network.get_parameter(INJECTOR_ID_STIM_CURRENT))
        self.NoizeStimCurrentSpinBox.setValue(self.__network.get_parameter(INJECTOR_ID_NOIZE_STIM_CURRENT))
        self.SynStepSpinBox.setValue(self.__network.get_parameter(INJECTOR_ID_SYN_STEP))
        self.UThresholdSpinBox.setValue(self.__network.get_parameter(INJECTOR_ID_STIM_THRESHOLD))
        self.VThresholdSpinBox.setValue(self.__network.get_parameter(INJECTOR_ID_BRAKE_THRESHOLD))
        self.StabilityLimitSpinBox.setValue(self.__network.get_parameter(INJECTOR_ID_STABILITY_LIMIT))
        self.StimRelaxTimeSpinBox.setValue(self.__network.get_parameter(INJECTOR_ID_STIM_RELAX_TIME))
        self.StabRelaxTimeSpinBox.setValue(self.__network.get_parameter(INJECTOR_ID_STABILITY_RELAX_TIME))
        self.ResistanceSpinBox.setValue(self.__network.get_parameter(INJECTOR_ID_RESISTANCE))
        self.RelaxedStimSpinBox.setValue(self.__network.get_parameter(INJECTOR_ID_RELAXED_STIM))
        self.ResMaxSpinBox.setValue(self.__network.get_parameter(INJECTOR_ID_RESOURCE_MAX))
        self.ResMinSpinBox.setValue(self.__network.get_parameter(INJECTOR_ID_RESOURCE_LIMIT))

        for i in range(INJECTOR_CONSTS_COUNT):
            self.__parameters_set.append(None)

        self.show()

    # Window UI
    def init_ui(self):
        self.RealTimeApplyParametersCheckBox.setChecked(True)
        self.RealTimeApplyParametersCheckBox.stateChanged.connect(self.sub_realtime_checkbox_state)
        self.ApplyNowButton.setEnabled(False)
        self.ApplyNowButton.clicked.connect(self.sub_applynow_button)
        self.ElectrodeSensitivitySlider.valueChanged.connect(self.sub_electrode_sensitivity_slider_move)
        self.StimCurrentSpinBox.valueChanged.connect(self.sub_stim_current_value)
        self.NoizeStimCurrentSpinBox.valueChanged.connect(self.sub_noize_stim_current)
        self.SynStepSpinBox.valueChanged.connect(self.sub_syn_step)
        self.UThresholdSpinBox.valueChanged.connect(self.sub_stim_threshold)
        self.VThresholdSpinBox.valueChanged.connect(self.sub_brake_threshold)
        self.StabilityLimitSpinBox.valueChanged.connect(self.sub_stability_limit)
        self.StimRelaxTimeSpinBox.valueChanged.connect(self.sub_stim_relax_time)
        self.StabRelaxTimeSpinBox.valueChanged.connect(self.sub_stability_relax_time)
        self.ResistanceSpinBox.valueChanged.connect(self.sub_resistance)
        self.RelaxedStimSpinBox.valueChanged.connect(self.sub_relaxed_stim)
        self.ResMaxSpinBox.valueChanged.connect(self.sub_resourse_max)
        self.ResMinSpinBox.valueChanged.connect(self.sub_resourse_limit)

    # override
    def closeEvent(self, event):
        self.__parent.NeuronParametersButton.setEnabled(True)

    # Message Box
    def message_box(self, text, title=MESSAGE_TEXT):
        QMessageBox.question(self, title, text, QMessageBox.Ok)

    # apply parameter
    def push(self, injector_id, value):
        self.__network.inject_parameter(injector_id, value)

    #subs
    def sub_realtime_checkbox_state(self, state):
        self.ApplyNowButton.setEnabled(not state)
        self.sub_applynow_button()

    def sub_applynow_button(self):
        self.__parent.worker.suspend()
        self.__parent.worker.join()
        for i in range(INJECTOR_CONSTS_COUNT):
            if not self.__parameters_set[i] is None:
                self.push(i, self.__parameters_set[i])
                self.__parameters_set[i] = None
        self.__parent.worker.resume()

    def sub_electrode_sensitivity_slider_move(self, value):
        self.ElectrodeSensitivityLabel.setText("Electrode sensitivity: " + str(value/10))
        inj_const = 0
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, (value/10))
        else:
            self.__parameters_set[inj_const] = (value/10)

    def sub_stim_current_value(self, value):
        inj_const = 1
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_noize_stim_current(self, value):
        inj_const = 2
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_syn_step(self, value):
        inj_const = 3
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_stim_threshold(self, value):
        inj_const = 4
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_brake_threshold(self, value):
        inj_const = 5
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_stability_limit(self, value):
        inj_const = 6
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_stim_relax_time(self, value):
        inj_const = 7
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_stability_relax_time(self, value):
        inj_const = 8
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_resistance(self, value):
        inj_const = 9
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_relaxed_stim(self, value):
        inj_const = 10
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_resourse_max(self, value):
        inj_const = 11
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

    def sub_resourse_limit(self, value):
        inj_const = 12
        if self.RealTimeApplyParametersCheckBox.isChecked():
            self.push(inj_const, value)
        else:
            self.__parameters_set[inj_const] = value

