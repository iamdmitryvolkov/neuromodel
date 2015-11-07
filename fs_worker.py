# File System worker methods (C) Dmitry Volkov 2015

# version 1.0 (12.10.2015)

import numpy

from os import remove, rename, listdir

from gui_consts import *
from injector_consts import *


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


def save_parameter(key, value):
    ky = key.replace(SETTING_KEY_SPLITTER, "")
    vl = str(value).replace(SETTING_KEY_SPLITTER, "")
    try:
        l = len(ky) + len(SETTING_KEY_SPLITTER)
        flag = False

        old_file = open(SETTINGS_FILEPATH, "tr")
        new_file = open(TEMPFILE, "tw")
        add = ""
        for line in old_file:
            if (ky + SETTING_KEY_SPLITTER) == line[:l]:
                new_file.write(add + ky + SETTING_KEY_SPLITTER + vl)
                flag = True
                add = "\n"
            else:
                new_file.write(add + line.strip("\n"))
                add = "\n"
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


def load_parameter(key, default_value=None):
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


def clear_settings():
    try:
        remove(SETTINGS_FILEPATH)
    except OSError:
        pass


def get_saved_files():
    templist = listdir(SAVES_FILEPATH)
    result = []
    for i in templist:
        if i[-5:] == SAVEFILE_FORMAT:
            result.append(i[:-5])
    return result


def load_saved_file(filename):
    try:
        block = 1

        counter = 0
        array = []

        neurs = 0
        elects = 0

        noize_relative = False
        noize_val = 0

        syn_matrix = None
        el_matrix = None
        params = None
        state = None

        file = open(filename, "tr")
        for line in file:
            if block == 1:
                n = line.find("N")
                e = line.find("E")
                r = line.find("R")
                f = line.find("F")
                l = len(line)
                neurs = int(line[(n + 1):e])
                elects = int(line[(e + 1):max(r, f)])
                if r == -1:
                    noize_relative = False
                    noize_val = int(line[(f + 1):l])
                else:
                    noize_relative = True
                    noize_val = int(line[(r + 1):l])
                block = 2
            elif block == 2:
                array_line = []
                for num in line.split(", "):
                    array_line.append(float(num))
                array.append(array_line)
                counter += 1
                if counter == elects:
                    el_matrix = array
                    array = []
                    counter = 0
                    block = 3
            elif block == 3:
                array_line = []
                for num in line.split(", "):
                    array_line.append(float(num))
                array.append(array_line)
                counter += 1
                if counter == neurs:
                    syn_matrix = array
                    array = []
                    counter = 0
                    block = 4
            elif block == 4:
                array.append(int(line))
                counter += 1
                if counter == INJECTOR_CONSTS_COUNT:
                    params = array
                    array = []
                    counter = 0
                    block = 5
            elif block == 5:
                array_line = []
                for num in line.split(", "):
                    array_line.append(float(num))
                array.append(array_line)
                counter += 1
                if counter == neurs:
                    state = array
                    array = []
                    counter = 0
                    block = 6
        file.close()
        return [noize_relative, noize_val, syn_matrix, el_matrix, params, state]
    except Exception:
        fs_error()
        return None


def save_network_to_file(filename, noize_relative, noize_val, syn_matrix, el_matrix, params, state):
    try:
        neurs = len(syn_matrix)
        elects = len(el_matrix)
        if noize_relative:
            n_type = "R"
        else:
            n_type = "F"
        file = open(filename, "tw")
        file.write("N" + str(neurs) + "E" + str(elects) + n_type + str(noize_val) + "\n")
        for i in range(len(elects)):
            file.write(", ".join(str(j) for j in el_matrix[i]) + "\n")
        for i in range(len(neurs)):
            file.write(", ".join(str(j) for j in syn_matrix[i]) + "\n")
        for i in params:
            file.write(str(i))
        for i in range(len(neurs)):
            file.write(", ".join(str(j) for j in state[i]) + "\n")
        file.close()
        print("Successfully saved")
    except Exception:
        pass
