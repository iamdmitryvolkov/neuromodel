# Electrode for spike model of neuronal culture (C) Dmitry Volkov 2015

# version 2.0 (3.12.2015)


class Electrode:
    
    __charge = 0
    __params = None
    
    def __init__(self, params):
        self.__params = params

    def get_status(self):
        result = self.__charge >= self.__params.sensitivity
        self.__charge = 0
        return result

    def add_current(self, data):
        self.__charge += data
