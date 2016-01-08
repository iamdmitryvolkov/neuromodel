# Network params class (C) Dmitry Volkov 2015

# version 1.0 (3.12.2015)

from model.params_consts import *


class NetworkParams:

    # electrodes
    sensitivity = 2.0

    # neurons potential
    threshold = 7
    potential_relax_time = 7

    # neurons strength
    strength_min = 0.8
    strength_max = 1.5
    strength_relax_time = 20000

    # neurons resource
    resource_max_by_strength = 7.5

    # neurons other
    resistance = 5

    # connection
    syn_value_max = 5
    syn_value_min = 0.2
    connection_relax_time = 25000

    # network
    stimulation_current = 12

    def set(self, param_id, value):
        if param_id == ID_SENSITIVITY:
            self.sensitivity = value
        elif param_id == ID_THRESHOLD:
            self.threshold = value
        elif param_id == ID_POTENTIAL_RELAX_TIME:
            self.potential_relax_time = value
        elif param_id == ID_STRENGTH_MIN:
            self.strength_min = value
        elif param_id == ID_STRENGTH_MAX:
            self.strength_max = value
        elif param_id == ID_STRENGTH_RELAX_TIME:
            self.strength_relax_time = value
        elif param_id == ID_RESOURCE_MAX_BY_STRENGTH:
            self.resource_max_by_strength = value
        elif param_id == ID_RESISTANCE:
            self.resistance = value
        elif param_id == ID_SYN_VALUE_MAX:
            self.syn_value_max = value
        elif param_id == ID_SYN_VALUE_MIN:
            self.syn_value_min = value
        elif param_id == ID_CONNECTION_RELAX_TIME:
            self.connection_relax_time = value

    def get(self, param_id):
        if param_id == ID_SENSITIVITY:
            return self.sensitivity
        elif param_id == ID_THRESHOLD:
            return self.threshold
        elif param_id == ID_POTENTIAL_RELAX_TIME:
            return self.potential_relax_time
        elif param_id == ID_STRENGTH_MIN:
            return self.strength_min
        elif param_id == ID_STRENGTH_MAX:
            return self.strength_max
        elif param_id == ID_STRENGTH_RELAX_TIME:
            return self.strength_relax_time
        elif param_id == ID_RESOURCE_MAX_BY_STRENGTH:
            return self.resource_max_by_strength
        elif param_id == ID_RESISTANCE:
            return self.resistance
        elif param_id == ID_SYN_VALUE_MAX:
            return self.syn_value_max
        elif param_id == ID_SYN_VALUE_MIN:
            return self.syn_value_min
        elif param_id == ID_CONNECTION_RELAX_TIME:
            return self.connection_relax_time
        return None

    def get_state(self):
        result = []
        result.append(self.sensitivity)
        result.append(self.threshold)
        result.append(self.potential_relax_time)
        result.append(self.strength_min)
        result.append(self.strength_max)
        result.append(self.strength_relax_time)
        result.append(self.resource_max_by_strength)
        result.append(self.resistance)
        result.append(self.syn_value_max)
        result.append(self.syn_value_min)
        result.append(self.connection_relax_time)
        result.append(self.stimulation_current)
        return result

    def set_state(self, state):
        self.sensitivity = state[0]
        self.threshold = state[1]
        self.potential_relax_time = state[2]
        self.strength_min = state[3]
        self.strength_max = state[4]
        self.strength_relax_time = state[5]
        self.resource_max_by_strength = state[6]
        self.resistance = state[7]
        self.syn_value_max = state[8]
        self.syn_value_min = state[9]
        self.connection_relax_time = state[10]
        self.stimulation_current = state[11]
