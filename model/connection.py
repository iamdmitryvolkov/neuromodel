# Neurons connections (C) Dmitry Volkov 2015

# version 1.0 (17.11.2015)

import numpy

MU = 12
SIGMA = 3


class Connection:

    # links
    __params = None
    __from = None
    __to = None

    # signals
    __data = None
    __data_len = 0
    __pos = 0

    # connection
    __strength = 1

    def __init__(self, params, con_from, con_to):
        self.__params = params
        self.__from = con_from
        self.__to = [con_to]
        self.__data = []
        self.__data_len = int(numpy.random.normal(MU, SIGMA, 1)[0])
        if self.__data_len < 1:
            self.__data_len = 1
        for i in range(self.__data_len):
            self.__data.append(0)

    def step(self):
        val = self.__data[self.__pos] * self.__strength
        if val > 0:
            self.__strength += ((self.__params.syn_value_max - self.__strength) /
                                self.__params.connection_relax_time) * \
                               (sum(self.__data)/(self.__data_len * self.__params.strength_max))
        else:
            self.__strength -= ((self.__strength - self.__params.syn_value_min) /
                                (2 * self.__params.connection_relax_time)) * \
                               ((self.__data_len * self.__params.strength_max) / (sum(self.__data) + 1))
        for i in self.__to:
            i.add_current(val)
        self.__data[self.__pos] = self.__from.get_spike_value()
        self.__pos += 1
        if self.__pos == self.__data_len:
            self.__pos = 0

    def stimulate(self, current):
        self.__data[self.__pos] = current

    def push_electrode(self, electrode):
        self.__to.append(electrode)

    def get_state(self):
        result = [self.__strength]
        temp_pos = self.__pos
        for i in range(self.__data_len):
            result.append(self.__data[(temp_pos + i) % self.__data_len])
        return result

    def set_state(self, state):
        self.__data_len = len(state) - 1
        self.__pos = 0
        self.__data = state[1:]
        self.__strength = state[0]

    #TODO REMOVE
    def test(self):
        return self.__strength
