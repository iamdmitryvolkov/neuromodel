# Console UI to spike model of neuronal culture (C) Dmitry Volkov 2015

# version 1.1 (10.07.2015)

from shared_libs import fs_worker as fs
from model.network import *


class Callback:
    @staticmethod
    def draw_info(inform):
        result = "["
        for i in inform:
            if i:
                a = "1"
            else:
                a = " "
            result += a
        print(result + "]")


def value_error():
    print("Value Error")


def steps(str_count):
    try:
        count = int(str_count)
        if count > 0:
            for i in range(int(str_count)):
                ntw.step()
        else:
            value_error()
    except ValueError:
        value_error()


def add(string):
    try:
        if string[0] == "c":
            string_vals = string[3:].split(" ")
            vals = list(map(lambda x: int(x), string_vals))
            if len(vals) == 5 and vals[1] <= vals[2] and vals[3] <= vals[4] and \
                                    (vals[2] + 1 - vals[1]) * (vals[4] + 1 - vals[3]) >= vals[0]:
                if string[1:3] == "e ":
                    if vals[2] <= ntw.get_connections_count() and vals[4] <= ntw.get_electrodes_count():
                        ntw.add_connections(False, vals[0], vals[1] - 1, vals[2] - 1, vals[3] - 1, vals[4] - 1)
                        print("successfully added")
                    else:
                        value_error()
                elif string[1:3] == "n ":
                    if max(vals[2], vals[4]) <= ntw.get_neurons_count():
                        ntw.add_connections(True, vals[0], vals[1] - 1, vals[2] - 1, vals[3] - 1, vals[4] - 1)
                        print("successfully added")
                    else:
                        value_error()
                else:
                    value_error()
            else:
                value_error()
        elif string[0:2] == "e ":
            val = int(string[2:])
            ntw.add_electrodes(val)
            print("successfully added")
        elif string[0:2] == "n ":
            val = int(string[2:])
            ntw.add_neurons(val)
            print("successfully added")
        else:
            value_error()
    except Exception as e:
        print("Error:", e)


def info():
    print("Electrodes: " + str(ntw.get_electrodes_count()))
    print("Connections: " + str(ntw.get_connections_count()))
    print("Neurons: " + str(ntw.get_neurons_count()))
    nz = ntw.getNoize()
    if nz[0]:
        n_name = "Relative"
    else:
        n_name = "Fixed"
    print("Noize: " + n_name + "(" + str(nz[1]) + ")")


def show_help():
    print("'ace 10 1 20 3 15' - add 10 connections from connections in range 1-20 to electrodes in range 3-15")
    print("'acn 10 1 20 3 15' - add 10 connections from neurons in range 1-20 to neurons in range 3-15")
    print("'ae 10' - add 10 electrodes")
    print("'an 10' - add 10 neurons")
    print("blank string - 1 step")
    print("'h' - show help")
    print("number - do number of steps")
    print("'s1 1 1 1 1' - stimulate electrodes which numbers according with '1' in string after 's' symbol"
          "and do 1 step")
    print("'state load ${fname}' - load state from file 'fname'")
    print("'state save ${fname}' - save state to file 'fname'")
    print("'-' - close app")


def save_state(fname):
    try:
        st = ntw.get_state()
        fs.save_object(st, fname)
        print("Saved")
    except Exception as e:
        print("Error:", e)


def load_state(fname):
    try:
        st = fs.load_object(fname)
        ntw.set_state(st)
        print("Loaded")
    except Exception as e:
        print("Error:", e)


def stimulate(text):
    stim_list = []
    l = len(text)
    for i in range(ntw.get_electrodes_count()):
        if i == l:
            break
        if text[i] == '1':
            stim_list.append(i)
    ntw.stimulate(stim_list)
    ntw.step()


def noize(string):
    ok = True
    val = 0
    try:
        val = int(string[1:])
    except ValueError:
        value_error()
        ok = False
    if ok:
        if string[0] == 'f':
            if 0 <= val <= ntw.get_neurons_count():
                ntw.setNoize(False, val)
                print("Noize: Fixed(" + str(val) + ")")
            else:
                value_error()
        elif string[0] == 'r':
            if 0 <= val <= 100:
                ntw.setNoize(True, val)
                print("Noize: Relative(" + str(val) + ")")
            else:
                value_error()
        else:
            value_error()


# TODO : Remove noize after add new mechanism.
ntw = Network(Callback())
# test part
ntw.add_electrodes(30)
ntw.add_neurons(100)
ntw.add_connections(True, 2000, 0, 99, 0, 99)
ntw.add_connections(False, 150, 0, 1999, 0, 29)
ntw.setNoize(True, 5)
# end test part
print("Model started")
while bool(1):
    inpt = input(">")
    if len(inpt) > 0:
        if inpt == '-':
            break
        elif inpt[0] == 's':
            if inpt[0:11] == "state save ":
                save_state(inpt[11:])
            elif inpt[0:11] == "state load ":
                load_state(inpt[11:])
            else:
                stimulate(inpt[1:])
        elif inpt[0] == 'a':
            add(inpt[1:])
        elif inpt == 'i':
            info()
        elif inpt[0] == 'n':
            noize(inpt[1:])
        elif inpt == 'h':
            show_help()
        else:
            steps(inpt)
    else:
        ntw.step()
