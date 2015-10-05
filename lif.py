# Neuron for spike model of neuronal culture (C) Dmitry Volkov 2015

# version 1.1 (10.07.2015)


import math
from injector_consts import *

class Neuron:
    
    __uThreshold = 7 #threshold of neuron's potential
    __vThreshold = 7 #brake threshold
    
    __stabilityLimit = 10 #beta
    __stability = 0 #s
    
    __uPotential = 0 #u
    __brakePotential = 0 #v
    
    __uRelaxTime = 7 #tao_m
    __sRelaxTime = 70 #tao_s
    
    __resistance = 5 #R
    __relaxedUPotential = 0 #u_r
    
    #new data for next step
    __sinapseCurrent = 0 #I_synap
    __stimulationCurrent = 0 #I_stim
    __nextBrakePotential = 0 #v
    
    __stabScaleFactor = 1
    __membraneResourceMax = 10
    __membraneResource = 10
    __membraneResourceLimit = 2


    def __init__(self):
        self.__stabScaleFactor = -4.6/self.__stabilityLimit
        self.__membraneResource = self.__membraneResourceMax

    def reinit(self):
        self.__membraneResource = self.__membraneResourceMax
        self.__stability = 0
        self.__uPotential = 0
        self.__brakePotential = 0

    def stabilityScale(self):
        return math.pow(math.e,self.__stability*self.__stabScaleFactor)
    
    def stimulate(self, current):
        self.__stimulationCurrent = current
    
    def getSpikeStatus(self):
        return ((self.__uPotential >= self.__uThreshold) and (self.__brakePotential < self.__vThreshold) and (self.__membraneResource > self.__membraneResourceLimit))
    
    def getStability(self):
        return self.__stability
    
    def setSinapseCurrent(self, data):
        self.__sinapseCurrent = data
        
    def getThreshold(self):
        return self.__uThreshold
    
    def setStabilityInfo(self, info):
        j = 0
        s = 0
        for i in info:
            if (i < self.__stability):
                j = j + 1
                s = s - i
        s = s + j * self.__stability
        self.__nextBrakePotential = s
        
    def step(self):
        
        #membraneResource [in/de]creasing
        if (self.getSpikeStatus()):
            self.__membraneResource = self.__membraneResource - 1
        else:
            self.__membraneResource = min(self.__membraneResource*(1+1/self.__membraneResourceMax), self.__membraneResourceMax)
        
        #calculating u potential
        if (self.__uPotential >= self.__uThreshold):
            self.__uPotential = 0
            #self.__stimPotential =  - self.__stimPotential
        
        u = - (self.__uPotential - self.__relaxedUPotential) + self.__resistance * (self.__sinapseCurrent + self.__stimulationCurrent)
        
        self.__uPotential = self.__uPotential + u / self.__uRelaxTime
        
        #calculating v potential
        self.__brakePotential = self.__nextBrakePotential
        
        #calculating stability
        if (self.__uPotential >= self.__uThreshold):
            if (self.__brakePotential >= self.__vThreshold):
                b = - self.__stabilityLimit
            else:
                b = self.__stabilityLimit
        else:
            b = 0
        
        self.__stability = self.__stability + (b - self.__stability) * self.stabilityScale() / self.__sRelaxTime
        if (self.__stability < 0):
            self.__stability = 0
        
        #zeroing vars
        self.__sinapseCurrent = 0
        self.__stimulationCurrent = 0
        self.__nextBrakePotential = 0
        
        return b
        
    def inject_parameter(self, id, value):
        if (id == _INJECTOR_ID_BRAKE_THRESHOLD):
            self.__vThreshold = value
        elif (id == _INJECTOR_ID_RELAXED_STIM):
            self.__relaxedUPotential = value
        elif (id == _INJECTOR_ID_RESISTANCE):
            self.__resistance = value
        elif (id == _INJECTOR_ID_RESOURCE_LIMIT):
            self.__membraneResourceLimit = value
        elif (id == _INJECTOR_ID_RESOURCE_MAX):
            self.__membraneResourceMax = value
        elif (id == _INJECTOR_ID_STABILITY_LIMIT):
            self.__stabilityLimit = value
        elif (id == _INJECTOR_ID_STABILITY_RELAX_TIME):
            self.__sRelaxTime = value
        elif (id == _INJECTOR_ID_STIM_RELAX_TIME):
            self.__uRelaxTime = value
        elif (id == _INJECTOR_ID_STIM_THRESHOLD):
            self.__uThreshold = value

    def get_u_potential(self):
        return self.__uPotential

    def get_v_potential(self):
        return self.__brakePotential

    def get_stability(self):
        return self.__stability

    def get_membrane_resource(self):
        return self.__membraneResource