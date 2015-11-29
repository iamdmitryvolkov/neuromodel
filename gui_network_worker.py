# gui 2.0 network working thread
# 30.09.2015 Dmitry Volkov

# QT5
import threading
import time

# GUI
from gui_consts import *

from fs_worker import *


class NetworkWorker(threading.Thread):
    parent = None

    work = True
    running = False
    join_parameter = False
    suspend_running = False
    __save_activity = False
    __activity_file = None
    __close_act_file = False
    __finished = False

    def __init__(self, parent):
        self.parent = parent
        threading.Thread.__init__(self, target=self.main_loop)
        self.work = True
        self.start()

    def main_loop(self):
        while self.work:
            self.join_parameter = False
            if self.__close_act_file:
                close_act_file(self.__activity_file)
                self.__activity_file = None
            if self.running:
                if self.parent.ntw is not None:
                    self.parent.ntw.step()
            else:
                time.sleep(SLEEP_TIME_MAINLOOP)
        close_act_file(self.__activity_file)
        self.__finished = True

    # stop app
    def end_worker(self):
        self.work = False
        self.parent.print_now()

    # pause work
    def pause(self):
        self.running = False
        self.join()
        self.parent.print_now()
        self.__close_act_file = True

    # start work
    def go(self):
        self.running = True

    # flip working
    def flip_running(self):
        self.running = not self.running
        self.parent.print_now()
        if not self.running:
            self.__close_act_file = True

    # model output callback
    def draw_info(self, info):
        # save activity to file
        if self.__save_activity:
            if self.__activity_file is None:
                self.__activity_file = get_act_file(ACTYVITY_FILE)
            write_to_act_file(self.__activity_file, info)
        # send data to buffered printer
        result = "["
        for i in info:
            if i:
                a = "1"
            else:
                a = " "
            result += a
        self.parent.print_data(result + "]")

    # suspend working status
    def suspend(self):
        self.suspend_running = self.running
        if not self.running:
            self.__close_act_file = True

    # stop suspend
    def resume(self):
        self.running = self.suspend_running
        self.suspend_running = False

    def join(self):
        self.join_parameter = True
        while self.join_parameter and (not self.__finished):
            time.sleep(SLEEP_TIME_JOIN)

    def set_save_to_file(self, flag):
        self.__save_activity = flag
