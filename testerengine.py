# Network testing module (C) Dmitry Volkov 2015

# version 1.0 (8.07.2015)

import time
import queue
from task import *
from network import *

class TesterEngine:
    # const
    __SLEEP_TIME = 60  # sec
    __WORK_TIME = 15 * 60  # sec
    __TASK_FILENAME = "testerengine/tasks.txt"
    __LOG_FILENAME = "testerengine/log.txt"

    # var
    __stop_time = 0
    __task_queue = None
    __current_task = 0
    __errors = []
    __state = "Working"
    __last_screen_text = ""
    __data = []

    __changes_available = True
    __task_file = None
    __log_file = None

    # constructor
    def __init__(self):
        self.__task_file = open(self.__TASK_FILENAME, "tw")
        self.__task_queue = queue.Queue()

    # sleep anti-overheat function
    def __sleep(self):
        self.print_state(self.__last_screen_text + " - sleep" ,savelast = False)
        time.sleep(self.__SLEEP_TIME)
        self.__stop_time = int(time.time()) + self.__WORK_TIME
        self.print_state(self.__last_screen_text, savelast = False)

    # add task
    def add_task(self, task):
        if self.__changes_available:
            self.__task_queue._put(task)
            self.__task_file.write(task.get_name() + "\n")
        else:
            raise Exception("Changes already unavailable. Please reinitialize engine and try again")

    # start work
    def start(self):
        self.__stop_time = int(time.time()) + self.__WORK_TIME
        self.__changes_available = False
        self.__task_file.close()
        self.__log_file = open(self.__LOG_FILENAME, "ta")

        # write log
        startstr = time.strftime("%H:%M:%S Test started")
        self.__log_file.write("\n" + "=" * len(startstr) + "\n")
        self.__log_file.write(startstr + "\n")
        self.__log_file.write("=" * len(startstr) + "\n")

        self.__work()

        #final text
        errornames = ""
        for i in self.__errors:
            errornames = errornames + "\n" + i
        self.__write_log("Working finished.\nTotal tasks: " + str(self.__current_task) + "\nErrors: " + str(len(self.__errors)) + errornames)
        self.__log_file.close()

    # main worker
    def __work(self):
        neurs = [0,5,18]
        elects = [0]
        ele_marix = self.load_matrix("matrix/ele.txt")
        neu_marix = self.load_matrix("matrix/neu.txt")
        ntw = None
        id = 13
        values = None
        while (not self.__task_queue.empty()):
            task = self.__task_queue.get_nowait()
            self.__current_task = self.__current_task + 1
            for i in range(3):
                self.__write_log("Task: " + task.get_name() + " started. attempt: " + str(i))
                values = task.get_values()
                steps = task.get_time()
                percent_steps = int(steps/100)
                for j in range(len(values)):
                    step = 0
                    next_percent = 0
                    # preparing
                    self.print_state("Attempt: " + str(i) + "/3 Value: " + str(j) + "/" + str(len(values))  + " Preparing to start")
                    self.__data = []
                    ntw = Network(0,0,0,0,self)
                    ntw.ele_matrix_put(ele_marix)
                    ntw.neu_matrix_put(neu_marix)
                    ntw.setNoize(False, 5)
                    id = task.get_id()
                    if (id < 13):
                        ntw.inject_parameter(id, values[j])
                    elif(id == 14):
                        ntw.setNoize(False, values[j])
                    elif(id == 15):
                        if (values[j] != 0):
                            ntw.addConnections(True, values[j], 0, 99, 0, 99)
                    elif(id == 16):
                        if (values[j] != 0):
                            ntw.addConnections(False, values[j], 0, 99, 0, 29)
                    self.print_state("Attempt: " + str(i+1) + "/3 Value: " + str(j+1) + "/" + str(len(values))  + " Preparing completed")
                    self.__write_log("Task: " + task.get_name() + " Attempt: " + str(i+1) + " Value: " + str(j+1) + " Preparing completed")
                    # working
                    while(step < steps):
                        if (time.time() < self.__stop_time):
                            ntw.step()
                            if (id == 17):
                                l = []
                                for k in elects:
                                    l.append(ntw.get_electrode_current(k))
                                for k in neurs:
                                    l.append(ntw.get_membrane_resource(k))
                                    l.append(ntw.get_spike_status(k))
                                    l.append(ntw.get_stability(k))
                                    l.append(ntw.get_u_potential(k))
                                    l.append(ntw.get_v_potential(k))
                                self.__data.append(l)
                            step = step + 1
                            if (step >= next_percent):
                                self.print_state("Attempt: " + str(i+1) + "/3 Value: " + str(j+1) + "/" + str(len(values))  + " Working: " + str(int(100*step/steps)) + "%")
                                next_percent = next_percent + percent_steps
                        else:
                            self.__sleep()
                    self.__write_log("Task: " + task.get_name() + " Attempt: " + str(i+1) + " Value: " + str(j+1) + " Working completed")
                    #post-processing
                    self.print_state("Attempt: " + str(i+1) + "/3 Value: " + str(j+1) + "/" + str(len(values))  + " finished. Processing data")
                    self.process_data(task.get_name() + " " + str(i+1) + " [" + str(values[j]) + "]",id == 4)
                    self.__write_log("Task: " + task.get_name() + " Attempt: " + str(i+1) + " Value: " + str(j+1) + " completed")
        print('\rAll tasks completed' + 61*" ")

    def process_data(self, name, motives_work):
        density = []
        file = open("testerengine/" + name + " data.txt","tw")
        for i in self.__data:
            density.append(sum(i))
            file.write(", ".join(str(j) for j in i) + "\n")
        file.close()
        #file = open("testerengine/" + name + " density.txt","tw")
        #file.write(", ".join(str(j) for j in density) + "\n")
        #file.close()
        #spikes_per_ms = sum(density)/len(density)
        #spike_times = 0
        #for i in density:
        #    if (i != 0):
        #        spikes_times = spike_times + 1
        #if (spike_times != 0):
        #    pack_lim = int(sum(density)/spike_times)
        #else:
        #    pack_lim = 1
        #packs = []
        #for i in density:
        #    packs.append(i >= pack_lim)

        #file = open("testerengine/" + name + " packs.txt","tw")
        #file.write(", ".join(str(j) for j in packs) + "\n")
        #file.close()
        #for i in range(len(packs) - 1):
        #    pass

        #file = open("testerengine/" + name + " results.txt","tw")
        #file.write("Average spikes per millisecond: " + str(spikes_per_ms) + "\n")
        #file.write("Average pack length: " + str(pack_lim) + "\n")
        #file.write("Average time between packs: " + str(pack_lim) + "\n")
        #file.close()
        #
        #if (motives_work):
        #   pass

    # log writer
    def __write_log(self, text):
        time_ = time.strftime("%H:%M:%S ")
        spaces = len(time_) * " "
        lines = text.split("\n")
        self.__log_file.write(time_ + lines[0] + "\n")
        for i in lines[1:]:
            self.__log_file.write(spaces + i + "\n")
        self.__log_file.flush()

        # info input
    def drawInfo(self, info):
        self.__data.append(info)

    def print_state(self, text, savelast = True):
        if (savelast):
            self.__last_screen_text = text
        print("\r" + 70 * " ", end="", flush=True)
        print("\rTask: " + str(self.__current_task) + "/" + str(self.__current_task + self.__task_queue.qsize()) +\
              " " + text, end="", flush=True)

    def load_matrix(self, filename):
        file = open(filename,"tr")
        array = []
        max_len = 0

        for line in file:
            array_line = []
            for num in line.split(", "):
                array_line.append(float(num))
            l = len(array_line)
            array.append(array_line)
            if (l>max_len):
                max_len = l
        file.close()

        for i in range(len(array)):
            delta = max_len - len(array[i])
            for j in range(delta):
                array[i].append(0)

        return numpy.array(array)