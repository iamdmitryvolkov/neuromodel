# Electrode for spike model of neuronal culture (C) Dmitry Volkov 2015

# version 1.1 (10.07.2015)

class Electrode:
    
    __threshold = 1.0; #sensitivity of electrodes
    __charge = 0
    
    def __init__(self):
        pass
    
    #was activity on this electrode?
    def getData(self):
        return (self.__charge >= self.__threshold)
    
    #sending information about current potential
    def setData(self, data):
        self.__charge = data

    def reinit(self):
        self.__charge = 0

    def set_threshold(self, val):
        self.__threshold = val

    def get_charge(self):
        return self.__charge
