# Network testing task module (C) Dmitry Volkov 2015

# version 1.0 (8.07.2015)

# test id is number in table in plan
# 13 do nothing
# 14 change fixed noize level
# 15 extra connections
# 16 extra electrodes connections
# 17 potentials info

class Task:

    #const
    __values = []
    __id = 13
    __time = 0

    __name = ""

    def __init__(self, name, test_id):
        self.__name = name
        ids = {1:14, 2:1, 3:3, 4:15, 5:16, 6:4, 7:5, 8:6, 9:11, 10:12, 11:7, 12:8, 13:17}
        vals = {1:[2, 3, 5, 7, 10, 12, 15],\
                2:[5, 10, 20, 40],\
                3:[0.1, 0.5, 1, 1.5, 2, 3, 4],\
                4:[0, 300, 700, 1000, 2000, 3000, 5000],\
                5:[0, 1, 2, 3, 4, 5],\
                6:[3, 7, 10, 15],\
                7:[3, 7, 10, 15],\
                8:[5, 7, 10, 15],\
                9:[5, 10, 15],\
                10:[0, 2, 5],\
                11:[3, 7, 15, 50],\
                12:[10, 35, 70, 150],
                13:[42]}
        self.__values = vals[test_id]
        self.__id = ids[test_id]
        if (test_id == 4):
            self.__time = 60000
        else:
            self.__time = 20000

    def get_name(self):
        return self.__name

    def get_id(self):
        return self.__id

    def get_values(self):
        return self.__values

    def get_time(self):
        return self.__time