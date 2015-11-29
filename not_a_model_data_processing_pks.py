# pks adapter for data processing module (C) Dmitry Volkov 2015

# version 1.0 (22.11.2015)

import matplotlib.pyplot as plt
from os import listdir, mkdir
from fs_worker import *

SAVE = False

PKS_IN = "data/pks_data"
PKS_OUT = "data/pks_out"

ACTIVITY_EPSILON = 0.01
EVALUATIONS_EPSILON = 0.00001
AVERAGE_PACK_SECONDS = 1  # now not working
WINDOW_SIZE = 7
PACK_START_ACTIVITY = 30 # 137
PACK_END_ACTIVITY = 15 # 36
HISTOGRAM_COLUMNS = 7

# find next pack in data from index. returns start and end index. Can return None.
def find_pack(data, start_index):
    accumulator = 0
    if len(data) - WINDOW_SIZE > start_index:
        for i in range(WINDOW_SIZE):
            accumulator += sum(data[start_index + i])
    else:
        return None
    if accumulator >= PACK_START_ACTIVITY:
        pack = True
        pack_start = start_index
    else:
        pack = False
    for i in range(start_index, len(data) - WINDOW_SIZE):
        accumulator += (sum(data[i+WINDOW_SIZE]) - sum(data[i]))
        if not pack:
            if accumulator >= PACK_START_ACTIVITY:
                pack = True
                pack_start = i+1
        else:
            if accumulator <= PACK_END_ACTIVITY:
                return pack_start, (i+1)
    if pack:
        return pack_start, len(data)
    else:
        return None


# calculate population activity of pack. average data in some seconds
def get_population_activity(data, indexes):
    result2 = []
    pack = data[indexes[0]:indexes[1]]
    for moment in pack:
        result2.append(sum(moment))
    return result2


def get_relative_frequency(population):
    result = []
    # calc number of different values
    values = []
    for i in population:
        founded = False
        for j in values:
            if abs(i - j) < ACTIVITY_EPSILON:
                founded = True
                break;
        if not founded:
            values.append(i)
    values.sort()
    for i in values:
        freq = 0
        for j in population:
            if abs(i - j) < ACTIVITY_EPSILON:
                freq += 1
        result.append(freq)
    return result, values


def transform_data(dv):
    data = dv[0]
    vals = dv[1]
    m = max(vals)
    step = (m + ACTIVITY_EPSILON)/HISTOGRAM_COLUMNS
    fdata = []
    fvals = []
    val = 0
    j = 0
    max_j = len(vals)
    for i in range(HISTOGRAM_COLUMNS):
        fvals.append(val)
        val = val + step
        summ = 0
        while j < max_j and vals[j] < val:
            summ += data[j]
            j += 1
        fdata.append(summ)
    return fdata, fvals


def normilize_frequency(data):
    s = sum(data)
    result = []
    for i in data:
        result.append(i/s)
    return result


def accumulate_frequency(freq):
    accumulator = 0
    result = []
    for i in freq:
        accumulator += i
        result.append(accumulator)
    return result


def draw_data(data, vals, m, d, a, e, name, folder):
    width = vals[1]
    ax = plt.gca()
    ax.set_axis_bgcolor("#221818")
    plt.bar(vals, data, width, color="#EEEECC")
    plt.xlim([0, vals[len(vals) - 1] + width])
    plt.ylim([0, 1])
    text = "m: " + str(m) + "\nD: " + str(d) + "\na: " + str(a) + "\nk: " + str(e)
    plt.figtext(0.13, 0.77, text, color="#EE2222")
    plt.savefig(PKS_OUT + "/" + folder + "/pack_" + name)
    plt.close()


def draw_activity(data, name, folder):
    max_data = max(data)
    width = 1
    ax = plt.gca()
    ax.set_axis_bgcolor("#221818")
    plt.bar(list(range(len(data))), data, width, color="#EEEECC")
    plt.xlim([0, len(data)])
    plt.ylim([0, max_data])
    text = "length: " + str(len(data)) + "\nmax_value: " + str(max_data)
    plt.figtext(0.13, 0.77, text, color="#EE2222")
    plt.savefig(PKS_OUT + "/" + folder + "/pack_" + name)
    plt.close()


def get_evaluations(data):
    m = 0
    for i in range(len(data)):
        m += (i * data[i])
    d = 0
    for i in range(len(data)):
        d += (pow((i - m), 2) * data[i])
    a = 0
    e = 0
    if abs(d) > EVALUATIONS_EPSILON:
        for i in range(len(data)):
            a += (pow((i - m), 3) * data[i])
        a /= pow(d, 3/2)
        for i in range(len(data)):
            e += (pow((i - m), 4) * data[i])
        e = e/pow(d, 4/2) - 3
    return m, d, a, e


def work(data, i, name):
    freq = get_relative_frequency(data)
    freq_transformed = transform_data(freq)
    vals = freq_transformed[1]
    dt = normilize_frequency(freq_transformed[0])
    dta = accumulate_frequency(dt)
    m, d, a, e = get_evaluations(dt)
    m = round(m, 3)
    d = round(d, 3)
    a = round(a, 3)
    e = round(e, 3)
    draw_data(dt, vals, m, d, a, e, str(i), name)
    draw_data(dta, vals, m, d, a, e, str(i) + "a", name)
    if i != 0:
        draw_activity(data, str(i) + "activity", name)


def process(data, name):
    print(name, flush=True)
    mkdir(PKS_OUT + "/" + name)
    alldata = data
    packs = []
    start_ind = 0
    flag = True
    while flag:
        pack = find_pack(alldata, start_ind)
        if pack is not None:
            packs.append(pack)
            start_ind = pack[1]
        else:
            flag = False
    print("\ndrawing all activity", flush=True)
    work(get_population_activity(alldata, (0, len(alldata))), 0, name)
    print("founded " + str(len(packs)) + " packs", flush=True)
    for i in range(len(packs)):
        print("\rProcessing: " + str(i+1) + "/" + str(len(packs)), flush=True, end="")
        work(get_population_activity(alldata, packs[i]), i+1, name)

# script
filelist = listdir(PKS_IN)
for fname in filelist:
    if SAVE:
        mtrx = load_pks(PKS_IN + "/" + fname)
        save_matrix(mtrx, PKS_OUT + "/" + fname[:-4] + "txt")
    else:
        #process(load_pks(PKS_IN + "/" + fname), fname[:-5])
        mtrx = load_pks(PKS_IN + "/" + fname)
        p_act = get_population_activity(mtrx, (0, len(mtrx)))
        print(get_relative_frequency(p_act))
