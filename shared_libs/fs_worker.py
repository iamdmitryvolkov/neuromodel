# File System worker methods (C) Dmitry Volkov 2015

# version 1.0 (12.10.2015)

import pickle
from os import remove, rename

SETTING_KEY_SPLITTER = "#"


def fs_error():
    print("Error working with filesystem")


def save_parameter(filename, key, value):
    tempfile = "tempfile"
    try:
        ind = filename.rindex('\\')
        tempfile = filename[:ind + 1] + tempfile
    except ValueError:
        try:
            ind = filename.rindex('/')
            tempfile = filename[:ind + 1] + tempfile
        except ValueError:
            pass
    ky = key.replace(SETTING_KEY_SPLITTER, "")
    vl = str(value).replace(SETTING_KEY_SPLITTER, "")
    try:
        l = len(ky) + len(SETTING_KEY_SPLITTER)
        flag = False

        old_file = open(filename, "tr")
        new_file = open(tempfile, "tw")
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
        remove(filename)
        rename(tempfile, filename)
    except Exception as e:
        file = open(filename, "tw")
        file.write(ky + SETTING_KEY_SPLITTER + vl)
        file.close()
        try:
            remove(tempfile)
        except OSError:
            pass


def load_parameter(filename, key, default_value=None):
    ky = key.replace(SETTING_KEY_SPLITTER, "")
    try:
        l = len(ky) + len(SETTING_KEY_SPLITTER)
        file = open(filename, "tr")
        for line in file:
            if (ky + SETTING_KEY_SPLITTER) == line[:l]:
                return line.strip()[l:]
    except Exception:
        pass
    return default_value


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
            if l > max_len:
                max_len = l
        file.close()

        for i in range(len(array)):
            delta = max_len - len(array[i])
            for j in range(delta):
                array[i].append(0)

        return array

    except Exception:
        fs_error()
        return None


def save_matrix(matrix, filename):
    try:
        file = open(filename, "tw")
        for i in range(len(matrix)):
            file.write(", ".join(str(j) for j in matrix[i]) + "\n")
        file.close()
    except Exception:
        fs_error()


def load_pks(filename):
    file = open(filename, "rb")
    data = pickle.load(file)
    file.close()
    keys = list(data.keys())
    ln = len(data[keys[0]])
    result = []
    for i in range(ln):
        line = []
        for key in keys:
            line.append(int(data[key][i]))
        result.append(line)
    return result


def save_object(obj, filename):
    file = open(filename, "wb")
    pickle.dump(obj, file)
    file.close()


def load_object(filename):
    file = open(filename, "rb")
    result = pickle.load(file)
    file.close()
    return result


def read_file(filename):
    try:
        file = open(filename, "tr")
        result = ""
        for line in file:
            result += line
        file.close()
        return result
    except Exception as e:
        fs_error()
        return str(e)


def write_file(filename, text):
    try:
        file = open(filename, "tw")
        file.write(text)
        file.close()
    except Exception:
        fs_error()
