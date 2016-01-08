# auto closable file for writing (C) Dmitry Volkov 2016

# version 1.0 (07.01.2016)

import threading
import time

TIME_TO_CLOSE = 5  # seconds


class AutoClosableFile:

    class Worker(threading.Thread):

        __file = None
        __pool = None

        def __init__(self, file, pool):
            self.__file = file
            self.__pool = pool
            threading.Thread.__init__(self, target=self.main_loop)
            self.start()

        def main_loop(self):
            while not self.__file.closed:
                while len(self.__pool) > 0:
                    self.__file.write(self.__pool.pop(0))
                time.sleep(TIME_TO_CLOSE)
                if len(self.__pool) == 0:
                    self.__file.close()

    __pool = None
    __file = None
    __worker = None

    def __init__(self, filename):
        self.__file = open(filename, "wb")
        self.__file.close()
        self.__pool = []

    def write(self, text):
        self.__pool.append(text)
        if self.__file.closed:
            name = self.__file.name
            self.__file = open(name, "at")
            self.Worker(self.__file, self.__pool)


