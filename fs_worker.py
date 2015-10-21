# File System worker methods (C) Dmitry Volkov 2015

# version 1.0 (12.10.2015)

import numpy

from os import remove, rename

from gui_consts import *

def fs_error():
    print("Error working with filesystem")


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

def save_matrix(matrix, filename):
    try:
        file = open(filename, "tw")
        for i in range(len(matrix)):
            file.write(", ".join(str(j) for j in matrix[i]) + "\n")
        file.close()
        print("Successfully saved")
    except Exception:
        fs_error()

def saveParameter(key, value):
    ky = key.replace(SETTING_KEY_SPLITTER, "")
    vl = str(value).replace(SETTING_KEY_SPLITTER, "")
    try:
        l = len(ky) + len(SETTING_KEY_SPLITTER)
        flag = False

        old_file = open(SETTINGS_FILEPATH, "tr")
        new_file = open(TEMPFILE, "tw")

        for line in old_file:
            if (ky + SETTING_KEY_SPLITTER) == line[:l]:
                new_file.write(ky + SETTING_KEY_SPLITTER + vl)
                flag = True
            else:
                new_file.write(line)
        old_file.close()
        if not flag:
            new_file.write("\n" + ky + SETTING_KEY_SPLITTER + vl)
        new_file.close()
        remove(SETTINGS_FILEPATH)
        rename(TEMPFILE, SETTINGS_FILEPATH)
    except Exception as e:
        file = open(SETTINGS_FILEPATH, "tw")
        file.write(ky + SETTING_KEY_SPLITTER + vl)
        file.close()
        try:
            remove(TEMPFILE)
        except OSError:
            pass

def loadParameter(key, default_value = None):
    ky = key.replace(SETTING_KEY_SPLITTER, "")
    try:
        l = len(ky) + len(SETTING_KEY_SPLITTER)
        file = open(SETTINGS_FILEPATH, "tr")
        for line in file:
            if (ky + SETTING_KEY_SPLITTER) == line[:l]:
                return line.strip()[l:]
    except Exception:
        pass
    return default_value

def clearSettings():
    try:
        remove(TEMPFILE)
    except OSError:
        pass
