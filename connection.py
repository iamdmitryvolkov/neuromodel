# Neurons connections (C) Dmitry Volkov 2015

# version 1.0 (17.11.2015)

import numpy

MU = 12
SIGMA = 3


class Connection:

    __from = None
    __to = None
    __data = []

    def __init__(self, con_from, con_to):
        self.__from = con_from
        self.__to = con_to
        for i in range(int(numpy.random.normal(MU, SIGMA, 1)[0])):
            arr = [0, 0, 0]
            self.__data.append(arr)
        if len(self.__data) == 0:
            arr = [0, 0, 0]
            self.__data.append(arr)

    def step(self):
        arr = [0, 0, 0]
        self.__data = self.__data[1:].append(arr)
