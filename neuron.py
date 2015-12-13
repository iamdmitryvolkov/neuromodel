# Neuron for spike model of neuronal culture (C) Dmitry Volkov 2015

# version 2.0 (02.12.2015)


class Neuron:

    # params
    __params = None

    # potential
    __potential = 0

    # strength
    __strength = 1

    # resource
    __resource = 7.5

    # incoming data
    __incoming_current = 0

    def __init__(self, params):
        self.__params = params

    def step(self):
        spike = self.get_spike_value()

        # potential
        if self.__potential >= self.__params.threshold:
            self.__potential = 0

        u = - self.__potential + self.__params.resistance * self.__incoming_current

        self.__potential += u / self.__params.potential_relax_time

        # resource
        res_max = self.__strength * self.__params.resource_max_by_strength
        if self.get_spike_value():
            self.__resource -= 1
        else:
            self.__resource = min(res_max, self.__resource * (1 + 1/res_max))

        # strength
        if spike:
            self.__strength += ((self.__params.strength_max - self.__strength) /
                                self.__params.strength_relax_time) *\
                               (res_max/(self.__resource + 1))
        else:
            self.__strength -= ((self.__strength - self.__params.strength_min) /
                                (2 * self.__params.strength_relax_time)) *\
                               ((self.__resource + 1)/res_max)

        # preparing to next step
        self.__incoming_current = 0

    def get_spike_value(self):
        if self.__potential >= self.__params.threshold and self.__resource > 1:
            return self.__strength
        else:
            return 0

    def add_current(self, value):
        self.__incoming_current += value

    def get_state(self):
        result = [self.__potential, self.__strength, self.__resource, self.__incoming_current]
        return result

    def set_state(self, state):
        self.__potential = state[0]
        self.__strength = state[1]
        self.__resource = state[2]
        self.__incoming_current = state[3]

