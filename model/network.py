# Spike model of neuronal culture (C) Dmitry Volkov 2015

# version 2.0 (02.12.2015)

import random

from model.connection import *
from model.network_params import *
from model.neuron import *
from model.electrode import *


class Network:

    __params = None
    __callback = None

    # data lists
    __neurons = None
    __electrodes = None
    __connections = None
    __connections_index_neurons = None
    __connections_index_electrodes = None

    # TODO: REMOVE IT
    __writer = None
    __relativeNoize = False
    __valNoize = 0
    noize = 0
    __noize_current = 15

    def __init__(self, callback):
        self.__neurons = []
        self.__electrodes = []
        self.__connections = []
        self.__connections_index_neurons = []
        self.__connections_index_electrodes = []
        self.__params = NetworkParams()
        self.__callback = callback

    # TODO: REMOVE IT
    def getNoize(self):
        return (self.__relativeNoize, self.__valNoize)

    def get_neurons_count(self):
        return len(self.__neurons)

    def get_electrodes_count(self):
        return len(self.__electrodes)

    def get_connections_count(self):
        return len(self.__connections)

    def add_electrodes(self, count):
        for i in range(count):
            self.__electrodes.append(Electrode(self.__params))

    def add_neurons(self, count):
        for i in range(count):
            self.__neurons.append(Neuron(self.__params))
        self.__recalcNoize()

    def add_connections(self, to_neurons, count, min_index_from, max_index_from, min_index_to, max_index_to):
        n_len = len(self.__neurons)
        c_len = len(self.__connections)
        e_len = len(self.__electrodes)
        if to_neurons:
            f_a = min(min_index_from, n_len - 1)
            f_b = min(max_index_from, n_len - 1)
            t_a = min(min_index_to, n_len - 1)
            t_b = min(max_index_to, n_len - 1)
            check_list = self.__connections_index_neurons
        else:
            f_a = min(min_index_from, c_len - 1)
            f_b = min(max_index_from, c_len - 1)
            t_a = min(min_index_to, e_len - 1)
            t_b = min(max_index_to, e_len - 1)
            check_list = self.__connections_index_electrodes
        connections = [(f, t) for f in range(f_a, f_b + 1) for t in range(t_a, t_b + 1)]
        connections = list(filter(lambda x: x not in check_list, connections))
        if to_neurons:
            connections = list(filter(lambda x: x[0] != x[1], connections))
        random.shuffle(connections)
        for con in connections[:count]:
            if to_neurons:
                self.__connections.append(Connection(self.__params, self.__neurons[con[0]], self.__neurons[con[1]]))
            else:
                self.__connections[con[0]].push_electrode(self.__electrodes[con[1]])
            check_list.append(con)

    # TODO: remove this
    def setNoize(self, relative, value):
        self.__valNoize = value
        self.__relativeNoize = relative
        self.__recalcNoize()

    # TODO: remove this
    def __recalcNoize(self):
        if self.__relativeNoize:
            self.noize = int(self.__valNoize * self.get_neurons_count() / 100)
        else:
            self.noize = self.__valNoize

    def step(self):
        # TODO: Remove noize part
        neurs = len(self.__neurons)

        # noize
        noizeList = list(range(neurs))  # pacemaker test
        random.shuffle(noizeList)
        for i in noizeList[:self.noize]:
            self.__neurons[i].add_current(self.__noize_current)

        for con in self.__connections:
            con.step()
            # todo remove it
        #summ = 0
        #for neu in self.__neurons:
        #    summ += int(neu.get_spike_value() > 0) #neu.test()
        for neu in self.__neurons:
            neu.step()

        # drawing information to screen
        line = []
        for i in self.__electrodes:
            if i.get_status():
                line.append(1)
            else:
                line.append(0)
        #print(summ, end="")
        self.__callback.draw_info(line)


    def stimulate(self, list):
        stimulation_list = []
        for i in self.__connections_index_electrodes:
            if i[1] in list:
                stimulation_list.append(i[0])
        for i in stimulation_list:
            self.__connections[i].stimulate(self.__params.stimulation_current)

    def set_parameter(self, id, value):
        self.__params.set(id, value)

    def get_parameter(self, id):
        return self.__params.get(id)

    def get_state(self):
        header = [len(self.__neurons), len(self.__connections), len(self.__electrodes)]
        result = [header]
        result.append(self.__params.get_state())
        result.append(self.__connections_index_electrodes)
        result.append(self.__connections_index_neurons)
        for neu in self.__neurons:
            result.append(neu.get_state())
        for con in self.__connections:
            result.append(con.get_state())
        return result

    def set_state(self, state):
        header = state[0]
        params_state = state[1]
        index_electrodes = state[2]
        index_neurons = state[3]
        self.__params.set_state(params_state)
        n_len = header[0]
        c_len = header[1]
        e_len = header[2]
        self.__electrodes = []
        self.add_electrodes(e_len)
        self.__neurons = []
        self.add_neurons(n_len)
        for i in range(n_len):
            self.__neurons[i].set_state(state[4 + i])
        self.__connections = []
        self.__connections_index_electrodes = index_electrodes
        self.__connections_index_neurons = index_neurons
        for pair in index_neurons:
            self.__connections.append(Connection(self.__params, self.__neurons[pair[0]], self.__neurons[pair[1]]))
        for pair in index_electrodes:
            self.__connections[pair[0]].push_electrode(self.__electrodes[pair[1]])
        shift = 4 + n_len
        for i in range(c_len):
            self.__connections[i].set_state(state[shift + i])

