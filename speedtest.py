# Test for model working speed (C) Dmitry Volkov 2015

# version 1.0 (2.12.2015)

from fs_worker import *
from network import *
import time

NOIZE_TYPE = True
NOIZE_VAL = True
MATRIX_PATH = "matrix/neu.txt"
ELE_PATH = "matrix/ele.txt"


class NullCallback:

    def draw_info(self, info):
        pass

callback = NullCallback()
ntw = Network(callback)
ntw.setNoize(NOIZE_TYPE, NOIZE_VAL)
ntw.add_neurons(100)
ntw.add_electrodes(30)
ntw.add_connections(True, 2000, 0, 99, 0, 99)
ntw.add_connections(False, 150, 0, 1999, 0, 29)

# test
start = int(round(time.time() * 1000))
for i in range(1000):
    ntw.step()
finish = int(round(time.time() * 1000))

print(finish - start, "ms")
