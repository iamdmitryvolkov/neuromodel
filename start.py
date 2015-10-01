# Console UI to spike model of neuronal culture (C) Dmitry Volkov 2015

# version 1.1 (10.07.2015)

import numpy
from network import *

ntw = Network(1, 1, 0, 0);


def valErr():
    print("Value Error")


def steps(textString):
    try:
        for i in range(int(textString)):
            ntw.step()
    except ValueError:
        valErr()


def noize(textString):
    ok = True
    try:
        val = int(textString[1:])
    except ValueError:
        valErr()
        ok = False
    if ok:
        if (textString[0] == 'f'):
            if (val <= ntw.getNeuronsCount()):
                ntw.setNoize(False, val)
            else:
                valErr()
        elif (textString[0] == 'r'):
            if (val <= 100):
                ntw.setNoize(True, val)
            else:
                valErr()
        else:
            valErr()


def stim(textString):
    elist = []
    l = len(textString)
    for i in range(ntw.getElectrodesCount()):
        if i == l:
            break;
        if (textString[i] == '1'):
            elist.append(i)
    ntw.stimulate(elist)
    ntw.step()


def choose(textString):
    if (textString == 'a'):
        ntw.setAllActive()
    else:
        separator = textString.find('-')
        if (separator != -1):
            try:
                val1 = int(textString[:separator])
                val2 = int(textString[(separator + 1):])
                if ((val1 > 0) and (val2 > 0) and (val2 >= val1) and (val2 <= ntw.getNeuronsCount())):
                    ntw.setActiveParts(val1 - 1, val2 - 1)
                else:
                    valErr()
            except ValueError:
                valErr()
        else:
            valErr()


def add(textString):
    if (len(textString) > 0):
        if (textString[0] == 'n'):
            if (len(textString) < 7):
                valErr()
            else:
                if (textString[1] != ' '):
                    valErr()
                else:
                    vals = textString[2:].split(' ')
                    if (len(vals) < 3):
                        valErr()
                    else:
                        ok = True
                        try:
                            val1 = int(vals[0])
                            val2 = int(vals[1])
                            val3 = int(vals[2])
                            ok = (
                            (val1 >= 0) and (val2 >= 0) and (val3 >= 0) and (val2 < (val1 * ntw.getElectrodesCount())))
                        except ValueError:
                            valErr()
                            ok = False
                        if ok:
                            if (val3 == 0):
                                ntw.addNeurons(val1, val2, val3, 0, 0)
                            else:
                                if (len(vals) < 5):
                                    valErr()
                                else:
                                    ok = True
                                    try:
                                        val4 = int(vals[3])
                                        val5 = int(vals[4])
                                    except ValueError:
                                        valErr()
                                        ok = False
                                    if (ok and (val5 >= val4) and (val4 > 0) and (
                                        val5 <= ntw.getNeuronsCount() + val1) and (val3 <= (val5 + 1 - val4))):
                                        ntw.addNeurons(val1, val2, val3, val4 - 1, val5 - 1)
                                    else:
                                        valErr()
        elif (textString[0] == 'c'):
            if (len(textString) < 12):
                valErr()
            else:
                ok = True
                if (textString[1] == 'n'):
                    val1 = True
                elif (textString[1] == 'e'):
                    val1 = False
                else:
                    valErr()
                    ok = False
                if ok:
                    vals = textString[3:].split(' ')
                    if (len(vals) < 5):
                        valErr()
                    else:
                        try:

                            val2 = int(vals[0])
                            val3 = int(vals[1])
                            val4 = int(vals[2])
                            val5 = int(vals[3])
                            val6 = int(vals[4])
                        except ValueError:
                            valErr()
                            ok = False
                        if ok:
                            if ((val2 > 0) and (val3 > 0) and (val5 > 0) and (val4 >= val3) and (val6 >= val5) and (
                                val4 <= ntw.getNeuronsCount()) and (((val1) and (val6 <= ntw.getNeuronsCount())) or (
                                (not val1) and (val6 <= ntw.getElectrodesCount()))) and (
                                val2 < ((val6 + 1 - val5) * (val4 + 1 - val3)))):
                                ntw.addConnections(val1, val2, val3 - 1, val4 - 1, val5 - 1, val6 - 1)
                            else:
                                valErr()
        elif (textString[0] == 'e'):
            if (len(textString) < 5):
                valErr()
            else:
                if (textString[1] != ' '):
                    valErr()
                else:
                    vals = textString[2:].split(' ')
                    if (len(vals) < 2):
                        valErr()
                    else:
                        ok = True
                        try:
                            val1 = int(vals[0])
                            val2 = int(vals[1])
                            ok = ((val1 >= 0) and (val2 >= 0))
                        except ValueError:
                            valErr()
                            ok = False
                        if ok:
                            if (val2 == 0):
                                ntw.addElectrodes(val1, val2, 0, 0)
                            else:
                                if (len(vals) < 4):
                                    valErr()
                                else:
                                    ok = True
                                    try:
                                        val3 = int(vals[2])
                                        val4 = int(vals[3])
                                    except ValueError:
                                        valErr()
                                        ok = False
                                    if (ok and (val4 >= val3) and ((val4 + 1 - val3) >= val2) and (
                                        val3 > 0) and () and (val4 <= ntw.getNeuronsCount())):
                                        ntw.addElectrodes(val1, val2, val3 - 1, val4 - 1)
                                    else:
                                        valErr()
        else:
            valErr()
    else:
        valErr()


def info():
    print("Electrodes: " + str(ntw.getElectrodesCount()))
    print("Neurons: " + str(ntw.getNeuronsCount()))
    nz = ntw.getNoize()
    if nz[0]:
        nName = "Relative"
    else:
        nName = "Fixed"
    print("Noize: " + nName + "(" + str(nz[1]) + ")")
    an = ntw.getActiveParts()
    print("Activated neurons from " + str(an[0] + 1) + " to " + str(an[1] + 1))


# save/load modules
def electrodes(text_string):
    texts = text_string.split(" ", 1)
    if (texts[0] == 's'):
        save_matrix(ntw.ele_matrix_get(), texts[1])
    elif (texts[0] == 'l'):
        m = load_matrix(texts[1])
        if (not m is None):
            ntw.ele_matrix_put(m)
            print("Successfully loaded")
    else:
        valErr()


def neurons(text_string):
    texts = text_string.split(" ", 1)
    if (texts[0] == 's'):
        save_matrix(ntw.neu_matrix_get(), texts[1])
    elif (texts[0] == 'l'):
        m = load_matrix(texts[1])
        if (not m is None):
            ntw.neu_matrix_put(m)
            print("Successfully loaded")
    else:
        valErr()


def fs_error():
    print("Error working with filesystem")


def save_matrix(matrix, filename):
    try:
        file = open(filename, "tw")
        for i in range(len(matrix)):
            file.write(", ".join(str(j) for j in matrix[i]) + "\n")
        file.close()
        print("Successfully saved")
    except Exception:
        fs_error()


def load_matrix(filename):
    try:
        file = open(filename, "tr")
        array = []
        max_len = 0

        for line in file:
            array_line = []
            for num in line.split(", "):
                array_line.append(float(num))
            l = len(array_line)
            array.append(array_line)
            if (l > max_len):
                max_len = l
        file.close()

        for i in range(len(array)):
            delta = max_len - len(array[i])
            for j in range(delta):
                array[i].append(0)

        return numpy.array(array)

    except Exception:
        fs_error()
        return None


while bool(1):
    inpt = input(">")
    if (len(inpt) > 0):
        if (inpt[0] == '-'):
            break
        elif (inpt[0] == 'e'):
            electrodes(inpt[1:])
        elif (inpt[0] == 'm'):
            neurons(inpt[1:])
        elif (inpt[0] == 's'):
            stim(inpt[1:])
        elif (inpt[0] == 'c'):
            choose(inpt[1:])
        elif (inpt[0] == 'a'):
            add(inpt[1:])
        elif (inpt[0] == 'i'):
            info()
        elif (inpt[0] == 'n'):
            noize(inpt[1:])
        else:
            steps(inpt)
    else:
        ntw.step()
