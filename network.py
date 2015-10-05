# Spike model of neuronal culture (C) Dmitry Volkov 2015

# version 1.1 (10.07.2015)

import numpy
import random
import math
from lif import *
from electrode import *
from injector_consts import *


class Network:
    __draw = bool(0)
    __eleList = []
    __neuList = []
    __synMatrix = None
    __electMatrix = None
    # parameters
    __noizePerMillisecond = 0
    __synMax = 3.5  # maximum of synapse value
    __synMin = 0.01
    __stimCurrent = 20  # I
    __noize_stim_current = 10
    __syn_step = 1

    # noizeType
    __relativeNoize = False
    __valNoize = 0

    # active parts
    __activeMin = 0
    __activeMax = 0

    # gui
    __gui = None

    def __init__(self, electrodes=8, neuronsPerElectrod=9, electrodeEnteres=4, neuronsEnteres=15, parentGui=None):
        if parentGui != None:
            self.__draw = True
        else:
            self.__draw = False

        self.__gui = parentGui

        self.__syn_step = self.__synMax * 0.05
        temp = []
        neurons = electrodes * neuronsPerElectrod
        self.__activeMax = neurons - 1
        self.__synMatrix = numpy.zeros((neurons, neurons))
        random.seed(version=2)
        numbersList = list(range(neurons))

        for i in range(neurons):
            tm = Neuron()
            temp.append(tm)
            random.shuffle(numbersList)
            for j in range(neuronsEnteres):
                self.__synMatrix[i][numbersList[j]] = random.random()

        self.__neuList = temp
        temp = []
        self.__electMatrix = numpy.zeros((electrodes, neurons))

        for i in range(electrodes):
            tm = Electrode()
            temp.append(tm)
            numbersList = list(range(i * neuronsPerElectrod, (i + 1) * neuronsPerElectrod))
            random.shuffle(numbersList)
            for j in range(electrodeEnteres):
                self.__electMatrix[i][numbersList[j]] = random.random()

        self.__eleList = temp
        self.__normalizeSinapses()

    def getNoize(self):
        return (self.__relativeNoize, self.__valNoize)

    def getNeuronsCount(self):
        return len(self.__neuList)

    def getElectrodesCount(self):
        return len(self.__eleList)

    def addElectrodes(self, electrodesCount, neuronsCount, neuronMinIndex, neuronMaxIndex):
        neurons = len(self.__electMatrix[0])
        electrodes = len(self.__electMatrix)
        mtrx = numpy.zeros((electrodes + electrodesCount, neurons))
        mtrx[:electrodes] = self.__electMatrix
        for i in range(electrodesCount):
            e = Electrode()
            self.__eleList.append(e)
        self.__electMatrix = mtrx
        if (neuronsCount > 0):
            for i in range(electrodesCount):
                self.addConnections(False, neuronsCount, neuronMinIndex, neuronMaxIndex, electrodes + i, electrodes + i)

    def addNeurons(self, neuronsCount, electrodesConnections, neuronConnectionsCount, neuronMinIndex, neuronMaxIndex):
        neurons = len(self.__synMatrix)
        newNeurons = neurons + neuronsCount
        if (self.__activeMax == neurons - 1):
            self.__activeMax = newNeurons - 1
        for i in range(neuronsCount):
            t = Neuron()
            self.__neuList.append(t)
        mtrx = numpy.zeros((newNeurons, newNeurons))
        mtrx[:neurons, :neurons] = self.__synMatrix
        self.__synMatrix = mtrx
        mtrx = numpy.zeros((len(self.__eleList), newNeurons))
        mtrx[:, :neurons] = self.__electMatrix
        self.__electMatrix = mtrx
        if (neuronConnectionsCount > 0):
            for i in range(neuronsCount):
                self.addConnections(True, neuronConnectionsCount, 0, neurons - 1, neurons + i, neurons + i)
        if (electrodesConnections > 0):
            self.addConnections(False, electrodesConnections, neurons, newNeurons - 1, 0, len(self.__electMatrix) - 1)

    def addConnections(self, neurons, count, fromMin, fromMax, toMin, toMax):
        l = [(a, b) for a in range(fromMin, fromMax + 1) for b in range(toMin, toMax + 1)]
        random.shuffle(l)
        if neurons:
            for i in l[:count]:
                self.__synMatrix[i[1], i[0]] = random.random()
            p = self.getActiveParts()
            self.setAllActive()
            self.__normalizeSinapses()
            self.setActiveParts(p[0], p[1])
        else:
            for i in l[:count]:
                self.__electMatrix[i[1], i[0]] = random.random()

    def setActiveParts(self, minIndex, maxIndex):
        self.__activeMin = minIndex
        self.__activeMax = maxIndex
        self.__recalcNoize()

    def getActiveParts(self):
        return (self.__activeMin, self.__activeMax)

    def setAllActive(self):
        self.__activeMin = 0
        self.__activeMax = len(self.__neuList) - 1
        self.__recalcNoize()

    def setNoize(self, relative, value):
        self.__valNoize = value
        self.__relativeNoize = relative
        self.__recalcNoize()

    def __recalcNoize(self):
        if self.__relativeNoize:
            self.__noizePerMillisecond = int(float(self.__valNoize) / 100 * (self.__activeMax + 1 - self.__activeMin))
        else:
            self.__noizePerMillisecond = int(
                float(self.__valNoize * (self.__activeMax + 1 - self.__activeMin)) / (len(self.__neuList)))
            # print("Current noize: " + str(self.__noizePerMillisecond))

    def __connectionsCount(self, i):
        res = 0
        for j in self.__synMatrix[i]:
            if (j > (self.__synMin / 10)):
                res = res + 1
        return res

    def __normalizeSinapses(self):
        neurs = len(self.__neuList)
        for i in range(self.__activeMin, self.__activeMax + 1):
            d = math.sqrt(self.__connectionsCount(i)) * self.__neuList[i].getThreshold() / 2 - self.__neuList[
                                                                                                   i].getStability() / 4
            b = self.__synMatrix[i]
            summ = numpy.dot(b, numpy.transpose(b))
            if (summ > (self.__synMin / 10)):
                d = d / summ
                for j in range(self.__activeMin, self.__activeMax + 1):
                    self.__synMatrix[i][j] = self.__synMatrix[i][j] * d

    def step(self):
        neurs = len(self.__neuList)
        elects = len(self.__eleList)

        # noize
        noizeList = list(range(neurs))
        random.shuffle(noizeList)
        for i in noizeList[:(int(self.__noizePerMillisecond * ((self.__activeMax + 1 - self.__activeMin) / neurs)))]:
            self.__neuList[i].stimulate(self.__noize_stim_current)

        old = numpy.zeros((neurs, 1))

        for i in range(self.__activeMin, self.__activeMax + 1):
            old[i] = self.__neuList[i].getSpikeStatus()
        # print(numpy.dot(numpy.transpose(old),old))
        new = numpy.dot(self.__synMatrix, old)

        r = numpy.zeros((neurs, 1))
        for i in range(self.__activeMin, self.__activeMax + 1):
            self.__neuList[i].setSinapseCurrent(new[i][0])
            t = []
            for j in range(self.__activeMin, self.__activeMax + 1):
                if ((self.__synMatrix[i][j] > (self.__synMin / 10)) and (old[j][0])):
                    t.append(self.__neuList[j].getStability())
            self.__neuList[i].setStabilityInfo(t)
            r[i] = self.__neuList[i].step()

        for i in range(self.__activeMin, self.__activeMax + 1):
            if (r[i][0] > 0):
                for j in range(self.__activeMin, self.__activeMax + 1):
                    if (self.__synMatrix[i][j] > (self.__synMin / 10)):
                        if (old[j][0]):
                            self.__synMatrix[i][j] = min(
                                self.__synMatrix[i][j] + self.__syn_step * self.__neuList[j].stabilityScale(),
                                self.__synMax)
                        else:
                            self.__synMatrix[i][j] = max(
                                self.__synMatrix[i][j] - self.__syn_step * self.__neuList[j].stabilityScale(),
                                self.__synMin)
            elif (r[i][0] < 0):
                for j in range(self.__activeMin, self.__activeMax + 1):
                    if (self.__synMatrix[i][j] > (self.__synMin / 10)):
                        if (not old[j][0]):
                            self.__synMatrix[i][j] = min(
                                self.__synMatrix[i][j] + self.__syn_step * self.__neuList[j].stabilityScale(),
                                self.__synMax)
                        else:
                            self.__synMatrix[i][j] = max(
                                self.__synMatrix[i][j] - self.__syn_step * self.__neuList[j].stabilityScale(),
                                self.__synMin)
                            # min
        self.__normalizeSinapses()
        # we print new spike data!
        for i in range(self.__activeMin, self.__activeMax + 1):
            old[i] = self.__neuList[i].getSpikeStatus()
        new = numpy.dot(self.__electMatrix, old)
        for i in range(elects):
            self.__eleList[i].setData(new[i][0])

        # drawing information to screen
        if (not self.__draw):
            text = ""
            add = ""
            for i in self.__eleList:
                if i.getData():
                    add = "1"
                else:
                    add = " "
                text = text + add
            print(text)
        else:
            line = []
            for i in self.__eleList:
                if i.getData():
                    line.append(1)
                else:
                    line.append(0)

            self.__gui.drawInfo(line)

    def stimulate(self, ilist):
        for i in ilist:
            for j in range(len(self.__electMatrix[i])):
                if (self.__electMatrix[i][j] > (self.__synMin / 10)):
                    self.__neuList[j].stimulate(self.__stimCurrent * self.__electMatrix[i][j])

    # special testing methods
    def ele_matrix_get(self):
        return self.__electMatrix

    def neu_matrix_get(self):
        return self.__synMatrix

    def ele_matrix_put(self, matrix, zeros=True):
        # old sizes
        neurs = len(self.__neuList)
        elects = len(self.__eleList)
        # new sizes
        new_neurs = len(matrix[0])
        new_elects = len(matrix)

        # preparing electrodes
        delta = new_elects - elects
        if (delta >= 0):
            for i in range(delta):
                e = Electrode()
                self.__eleList.append(e)
            if (zeros):
                for i in range(elects):
                    self.__eleList[i].reinit()
        else:
            self.__eleList = self.__eleList[:delta]
            if (zeros):
                for i in range(new_elects):
                    self.__eleList[i].reinit()

        # preparing neurons
        delta = new_neurs - neurs
        if (delta >= 0):
            for i in range(delta):
                n = Neuron()
                self.__neuList.append(n)
            if (zeros):
                for i in range(neurs):
                    self.__neuList[i].reinit()
            if (delta != 0):
                smatrix = numpy.zeros((new_neurs,new_neurs))
                smatrix[:neurs,:neurs] = self.__synMatrix
                self.__synMatrix = smatrix
        else:
            self.__neuList = self.__neuList[:delta]
            if (zeros):
                for i in range(new_neurs):
                    self.__neuList[i].reinit()

            self.__synMatrix = self.__synMatrix[:new_neurs,:new_neurs]
        if (delta != 0):
            self.setAllActive()

        self.__electMatrix = matrix

    def neu_matrix_put(self, matrix, zeros=True):
        # old size
        neurs = len(self.__neuList)
        elects = len(self.__eleList)
        # new size
        new_neurs = len(matrix)

        # preparing neurons and electrodes
        delta = new_neurs - neurs
        if (delta >= 0):
            for i in range(delta):
                n = Neuron()
                self.__neuList.append(n)
            if (zeros):
                for i in range(neurs):
                    self.__neuList[i].reinit()
            if (delta != 0):
                smatrix = numpy.zeros((elects,new_neurs))
                smatrix[:,:neurs] = self.__electMatrix
                self.__electMatrix = smatrix
        else:
            self.__neuList = self.__neuList[:delta]
            if (zeros):
                for i in range(new_neurs):
                    self.__neuList[i].reinit()
            self.__electMatrix = self.__electMatrix[:,:delta]

        if (zeros):
            for i in range(elects):
                self.__eleList[i].reinit();

        self.__synMatrix = matrix

        if (delta != 0):
            self.setAllActive()

    def inject_parameter(self, id, value):
        if (id > 3):
            for i in self.__neuList:
                i.inject_parameter(id,value)
        elif(id == INJECTOR_ID_STIM_CURRENT):
            self.__stimCurrent = value
        elif(id == INJECTOR_ID_NOIZE_STIM_CURRENT):
            self.__noize_stim_current = value
        elif(id == INJECTOR_ID_SYN_STEP):
            self.__syn_step = value
        elif(id == 3):
            for i in self.__eleList:
                i.set_threshold(value)

    def get_spike_status(self, number):
        return self.__neuList[number].getSpikeStatus()

    def get_u_potential(self, number):
        return self.__neuList[number].get_u_potential()

    def get_v_potential(self, number):
        return self.__neuList[number].get_v_potential()

    def get_stability(self, number):
        return self.__neuList[number].get_stability()

    def get_membrane_resource(self, number):
        return self.__neuList[number].get_membrane_resource()

    def get_electrode_current(self, number):
        return self.__eleList[number].get_charge()

