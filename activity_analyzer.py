# Data processing module (C) Dmitry Volkov 2016

# version 1.0 (06.01.2016)

import sys
import matplotlib.pyplot as plt
from shared_libs import fs_worker as fs
from model.network import *

COMMANDS_TEMPLATE = ["-parameter", "-activity", "-graph", "-bpks", "-dynamics"]
EVALUATIONS_EPSILON = 0.0001
DATA_EPSILON = 0.01


def show_usage():
    print('''
    Usage: {command}
    command = cmd1 | cmd2 | cmd3 | cmd4 | cmd5
    cmd1 = -parameter <parameter_id> <value min> <value max> [step <step value. default = 1>]
    cmd2 = -activity [-drawall] <filename>
    cmd3 = -graph [-lims <y axis limit min> <y axis limit min>] <filename>
    cmd4 = -bpks {<filename>}
    cmd5 = -dynamics {<neuron number>}
    ''')


# returns start and end index of burst
def find_pack(data, start_index, params):
    w_size, ps, pe = params
    accumulator = 0
    if len(data) - w_size > start_index:
        for i in range(w_size):
            accumulator += sum(data[start_index + i])
    else:
        return None
    if accumulator >= ps:
        pack = True
        pack_start = start_index
    else:
        pack = False
    for i in range(start_index, len(data) - w_size):
        accumulator += (sum(data[i+w_size]) - sum(data[i]))
        if not pack:
            if accumulator >= ps:
                pack = True
                pack_start = i+1
        else:
            if accumulator <= pe:
                return pack_start, (i+1)
    if pack:
        return pack_start, len(data)
    else:
        return None


def get_population_activity(pack):
    result = []
    for moment in pack:
        result.append(sum(moment))
    return result


def transform_data(dv, columns):
    data = dv[0]
    vals = dv[1]
    m = max(vals)
    step = (m + DATA_EPSILON)/columns
    fdata = []
    fvals = []
    val = 0
    j = 0
    max_j = len(vals)
    for i in range(columns):
        fvals.append(val)
        val = val + step
        summ = 0
        while j < max_j and vals[j] < val:
            summ += data[j]
            j += 1
        fdata.append(summ)
    return fdata, fvals


# frequency is a tuple (<freq_value>, <value>)
def get_relative_frequency(population):
    result = []
    # calc number of different values
    values = []
    for i in population:
        founded = False
        for j in values:
            if abs(i - j) < DATA_EPSILON:
                founded = True
                break
        if not founded:
            values.append(i)
    values.sort()
    for i in values:
        freq = 0
        for j in population:
            if abs(i - j) < DATA_EPSILON:
                freq += 1
        result.append(freq)
    return result, values


def normalize_frequency(freq):
    data, vals = freq
    s = sum(data)
    result = []
    for i in data:
        result.append(i/s)
    return result, vals


def accumulate_frequency(freq):
    data, vals = freq
    accumulator = 0
    result = []
    for i in data:
        accumulator += i
        result.append(accumulator)
    return result, vals


def calculate_statistics_relative_freq(freq):
    data, vals = freq
    m = 0
    for i in range(len(data)):
        m += (vals[i] * data[i])
    d = 0
    for i in range(len(data)):
        d += (pow((vals[i] - m), 2) * data[i])
    a = 0
    e = 0
    if abs(d) > EVALUATIONS_EPSILON:
        for i in range(len(data)):
            a += (pow((vals[i] - m), 3) * data[i])
        a /= pow(d, 3/2)
        for i in range(len(data)):
            e += (pow((vals[i] - m), 4) * data[i])
        e = e/pow(d, 4/2) - 3
    return m, d, a, e


def calculate_statistics_sequence(data):
    rf = get_relative_frequency(data)
    nrf = normalize_frequency(rf)
    return calculate_statistics_relative_freq(nrf)


def analyze_activity(data, params):
    packs = []
    start_ind = 0
    flag = True
    while flag:
        pack = find_pack(data, start_ind, params)
        if pack is not None:
            packs.append(pack)
            start_ind = pack[1]
        else:
            flag = False
    all_length = len(data)
    packs_length = 0
    count = len(packs)
    if count == 0:
        count = 1
    for pack in packs:
        packs_length += (pack[1]-pack[0])
    bl = packs_length/count
    nb = (all_length - packs_length)/count
    bp = packs_length/all_length
    return bl, nb, bp


def draw_activity(in_data, name):
    data = get_population_activity(in_data)
    max_data = max(data)
    width = 1
    ax = plt.gca()
    ax.set_axis_bgcolor("#221818")
    plt.bar(list(range(len(data))), data, width, color="#EEEECC")
    plt.xlim([0, len(data)])
    plt.ylim([0, max_data])
    text = "length: " + str(len(data)) + "\nmax_value: " + str(max_data)
    plt.figtext(0.13, 0.77, text, color="#EEEECC")
    plt.savefig("output/analyzer/" + name)
    plt.close()


def draw_data(in_data, m, d, a, e, name):
    data, vals = in_data
    width = vals[1]
    ax = plt.gca()
    ax.set_axis_bgcolor("#221818")
    plt.bar(vals, data, width, color="#EEEECC")
    plt.xlim([0, vals[len(vals) - 1] + width])
    plt.ylim([0, 1])

    text = "m: " + str(m) + "\nD: " + str(d) + "\na: " + str(a) + "\nk: " + str(e)
    plt.figtext(0.13, 0.77, text, color="#EEEECC")
    plt.savefig("output/analyzer/pack " + name)
    plt.close()


def process_burst(data, index, columns):
    act = get_population_activity(data)
    freq = get_relative_frequency(act)
    freq_transformed = transform_data(freq, columns)
    dt = normalize_frequency(freq_transformed)
    dta = accumulate_frequency(dt)
    m, d, a, e = calculate_statistics_relative_freq(dt)
    m = round(m, 3)
    d = round(d, 3)
    a = round(a, 3)
    e = round(e, 3)
    draw_data(dt, m, d, a, e, str(index))
    draw_data(dta, m, d, a, e, str(index) + "a")


def parameter(task):
    id = task[0]
    mn = task[1]
    mx = task[2]
    if len(task) == 4:
        st = task[3]
    else:
        st = 1
    val = mn
    pool = [mn]
    while mx - mn - st > EVALUATIONS_EPSILON:
        mn += st
        pool.append(mn)
    pool.append(mx)

    fname = "analyzer_settings.txt"
    neurs = int(fs.load_parameter(fname, "NEURONS", 100))
    elects = int(fs.load_parameter(fname, "ELECTRODES", 30))
    cons = int(fs.load_parameter(fname, "CONNECTIONS", 2000))
    elecons = int(fs.load_parameter(fname, "ELECONS", 150))
    noize = int(fs.load_parameter(fname, "NOIZEVAL", 5))
    testtime = int(fs.load_parameter(fname, "TESTTIME", 500))
    tests = int(fs.load_parameter(fname, "TESTS", 10))
    wind_size = int(fs.load_parameter(fname, "WINDOWSIZE", 7))
    pstart = int(fs.load_parameter(fname, "PACKSTART", 79))
    pend = int(fs.load_parameter(fname, "PACKEND", 21))
    params = (wind_size, pstart, pend)

    data = []
    pool_burst_len = []
    pool_noburst_len = []
    pool_burst_percent = []

    class Callback:
        @staticmethod
        def draw_info(info):
            data.append(info)

    for i in range(len(pool)):
        sbl = 0
        snbl = 0
        sbp = 0
        for j in range(tests):
            data = []
            callback = Callback()
            ntw = Network(callback)
            ntw.add_neurons(neurs)
            ntw.add_electrodes(elects)
            ntw.add_connections(True, cons, 0, neurs - 1, 0, neurs - 1)
            ntw.add_connections(False, elecons, 0, cons - 1, 0, elects - 1)
            ntw.setNoize(True, noize)
            ntw.set_parameter(id, pool[i])
            for k in range(testtime):
                ntw.step()
            bl, nbl, bp = analyze_activity(data, params)
            sbl += bl
            snbl +=nbl
            sbp += bp
        sbl /= tests
        snbl /= tests
        sbp /= tests
        pool_burst_len.append(sbl)
        pool_noburst_len.append(snbl)
        pool_burst_percent.append(sbp)

    lims = [0, max(max(pool_burst_len), max(pool_noburst_len))]
    plt.xlabel("parameter " + str(id))
    plt.ylabel("burst period length")
    plt.ylim(lims)
    plt.plot(pool, pool_burst_len)
    plt.savefig("output/analyzer/id " + str(id) + " burst length" + ".png")
    plt.close()
    plt.xlabel("parameter " + str(id))
    plt.ylabel("interburst period length")
    plt.ylim(lims)
    plt.plot(pool, pool_noburst_len)
    plt.savefig("output/analyzer/id " + str(id) + " interburst length" + ".png")
    plt.close()
    plt.xlabel("parameter " + str(id))
    plt.ylabel("burst percent")
    plt.ylim([0, 1])
    plt.plot(pool, pool_burst_percent)
    plt.savefig("output/analyzer/id " + str(id) + " burst percent" + ".png")
    plt.close()
    output = "id {0}\nvalues: {1}\nburst length: {2}\ninterburst length: {3}\nburst percent {4}"\
        .format(id, pool, pool_burst_len, pool_noburst_len, pool_burst_percent)
    fs.write_file("output/analyzer/id " + str(id) + " testing results" + ".txt", output)


def activity(task):
    drawall = len(task) == 2
    fname = task[0]
    sfname = "analyzer_settings.txt"
    wind_size = int(fs.load_parameter(sfname, "WINDOWSIZE", 7))
    pstart = int(fs.load_parameter(sfname, "PACKSTART", 79))
    pend = int(fs.load_parameter(sfname, "PACKEND", 21))
    columns = int(fs.load_parameter(sfname, "HISTCOLUMNS", 7))
    params = (wind_size, pstart, pend)
    alldata = fs.load_matrix(fname)
    if alldata is not None:
        packs = []
        start_ind = 0
        flag = True
        while flag:
            pack = find_pack(alldata, start_ind, params)
            if pack is not None:
                packs.append(pack)
                start_ind = pack[1]
            else:
                flag = False

        packs = list(map(lambda x: alldata[x[0]:x[1]], packs))
        if drawall:
            draw_activity(alldata, "all activity")
        process_burst(alldata, 0, columns)
        for i in range(len(packs)):
            process_burst(packs[i], i+1, columns)
            draw_activity(packs[i], "pack " + str(i+1) + " activity")
    else:
        print("cannot read file '" + fname + "'", flush=True)


def graph(task):
    lims = len(task) != 1
    if lims:
        fname = task[2]
    else:
        fname = task[0]

    axis_name = fname
    try:
        fname_index = axis_name.rindex('\\') + 1
        axis_name = axis_name[fname_index:]
    except ValueError:
        pass
    try:
        fname_index = axis_name.rindex('/') + 1
        axis_name = axis_name[fname_index:]
    except ValueError:
        pass
    try:
        dot_index =axis_name.rindex('.')
        axis_name = axis_name[:dot_index]
    except ValueError:
        pass
    matrix_act = fs.load_matrix(fname)
    act = matrix_act[0]

    if act is not None:
        result_name = "output/analyzer/graph_" + axis_name
        plt.figure(figsize=(max(8, len(act)/50), 6))
        plt.xlabel("time")
        plt.ylabel(axis_name)
        if lims:
            plt.ylim(task[:2])
        plt.plot(act)
        plt.savefig(result_name + ".png")
        plt.close()

        stat = calculate_statistics_sequence(act)
        output = "m = {0}\nD = {1}\na = {2}\nk = {3}".format(stat[0], stat[1], stat[2], stat[3])
        fs.write_file(result_name + ".txt", output)
    else:
        print("cannot read file '" + fname + "'", flush=True)


def bpks(task):
    for fname in task:
        try:
            fs.save_matrix(fs.load_pks(fname), fname[:-4] + "txt")
        except Exception:
            print("error working with file '" + fname + "'", flush=True)


def dynamics(task):
    try:
        numbers = list(map(lambda x: int(x), task))

        fname = "analyzer_settings.txt"
        neurs = int(fs.load_parameter(fname, "NEURONS", 100))
        elects = int(fs.load_parameter(fname, "ELECTRODES", 30))
        cons = int(fs.load_parameter(fname, "CONNECTIONS", 2000))
        elecons = int(fs.load_parameter(fname, "ELECONS", 150))
        noize = int(fs.load_parameter(fname, "NOIZEVAL", 5))
        dtesttime = int(fs.load_parameter(fname, "DYNTESTTIME", 2000))

        data = []
        states = []
        for i in range(len(numbers)):
            states.append([])

        class Callback:
            @staticmethod
            def draw_info(info):
                data.append(info)

        callback = Callback()
        ntw = Network(callback)
        ntw.add_neurons(neurs)
        ntw.add_electrodes(elects)
        ntw.add_connections(True, cons, 0, neurs - 1, 0, neurs - 1)
        ntw.add_connections(False, elecons, 0, cons - 1, 0, elects - 1)
        ntw.setNoize(True, noize)

        for i in range(dtesttime):
            ntw.step()
            state = ntw.get_state()
            for j in range(len(numbers)):
                states[j].append(state[3 + numbers[j]])

        # processing data
        value_dynamics = []
        for n_states in states:
            potential = []
            strength = []
            resource = []
            incoming_current = []
            for state in n_states:
                potential.append(state[0])
                strength.append(state[1])
                resource.append(state[2])
                incoming_current.append(state[3])
            neuron_data = [potential, strength, resource, incoming_current]
            value_dynamics.append(neuron_data)

        fs.save_matrix(data, "output/analyzer/dynamics_activity.txt")
        for i in range(len(numbers)):
            fs.save_matrix([value_dynamics[i][0]], "output/analyzer/dynamics_" + str(numbers[i]) + "_potential" + ".txt")
            fs.save_matrix([value_dynamics[i][1]], "output/analyzer/dynamics_" + str(numbers[i]) + "_strength" + ".txt")
            fs.save_matrix([value_dynamics[i][2]], "output/analyzer/dynamics_" + str(numbers[i]) + "_resource" + ".txt")
            fs.save_matrix([value_dynamics[i][3]], "output/analyzer/dynamics_" + str(numbers[i]) + "_current" + ".txt")

    except Exception as e:
        print("error: " + str(e), flush=True)


# script starts here

# argument parser is a finite state machine
# -1 - parse error
# 0 - waiting new command
# 1 - command 1 (parameter) waiting id
# 2 - command 2 (activity) waiting drawall or filename
# 3 - command 3 (graph) waiting lim or filename
# 4 - command 4 (bpks) waiting filename or new command
# 5 - command 5 (dynamics) waiting neuron number or new command
# 11 - command 1. waiting val2
# 12 - command 1. waiting val2
# 13 - command 1. step or new command
# 21 - command 2. drawall. waiting filename
# 31 - command 3. waiting min limit
# 32 - command 3. waiting max limit
# 33 - command 3. waiting filename
# 41 - command 4. one or more argument was got
# 51 - command 5. one or more argument was got

state = 0
task_pool = []
task = []

for i in range(1, len(sys.argv)):
    arg = sys.argv[i]
    if state == 0:
        if arg == COMMANDS_TEMPLATE[0]:
            state = 1
            task.append(1)
        elif arg == COMMANDS_TEMPLATE[1]:
            state = 2
            task.append(2)
        elif arg == COMMANDS_TEMPLATE[2]:
            state = 3
            task.append(3)
        elif arg == COMMANDS_TEMPLATE[3]:
            state = 4
            task.append(4)
        elif arg == COMMANDS_TEMPLATE[4]:
            state = 5
            task.append(5)
        else:
            state = -1
    elif state == 1:
        try:
            task.append(int(arg))
            state = 11
        except Exception:
            state = -1
    elif state == 2:
        if arg == "-drawall":
            state = 21
        else:
            task.append(arg)
            task_pool.append(task)
            task = []
            state = 0
    elif state == 3:
        if arg == "-lims":
            state = 31
        else:
            task.append(arg)
            task_pool.append(task)
            task = []
            state = 0
    elif state == 4:
        if arg == COMMANDS_TEMPLATE[0]:
            task_pool.append(task)
            task = []
            state = 1
            task.append(1)
        elif arg == COMMANDS_TEMPLATE[1]:
            task_pool.append(task)
            task = []
            state = 2
            task.append(2)
        elif arg == COMMANDS_TEMPLATE[2]:
            task_pool.append(task)
            task = []
            state = 3
            task.append(3)
        elif arg == COMMANDS_TEMPLATE[3]:
            task_pool.append(task)
            task = []
            state = 4
            task.append(4)
        elif arg == COMMANDS_TEMPLATE[4]:
            task_pool.append(task)
            task = []
            state = 5
            task.append(5)
        else:
            task.append(arg)
            state = 41
    elif state == 5:
        if arg == COMMANDS_TEMPLATE[0]:
            task_pool.append(task)
            task = []
            state = 1
            task.append(1)
        elif arg == COMMANDS_TEMPLATE[1]:
            task_pool.append(task)
            task = []
            state = 2
            task.append(2)
        elif arg == COMMANDS_TEMPLATE[2]:
            task_pool.append(task)
            task = []
            state = 3
            task.append(3)
        elif arg == COMMANDS_TEMPLATE[3]:
            task_pool.append(task)
            task = []
            state = 4
            task.append(4)
        elif arg == COMMANDS_TEMPLATE[4]:
            task_pool.append(task)
            task = []
            state = 5
            task.append(5)
        else:
            task.append(arg)
            state = 51
    elif state == 11:
        try:
            task.append(float(arg))
            state = 12
        except Exception:
            state = -1
    elif state == 12:
        try:
            task.append(float(arg))
            state = 13
        except Exception:
            state = -1
    elif state == 13:
        if arg == COMMANDS_TEMPLATE[0]:
            task_pool.append(task)
            task = []
            state = 1
            task.append(1)
        elif arg == COMMANDS_TEMPLATE[1]:
            task_pool.append(task)
            task = []
            state = 2
            task.append(2)
        elif arg == COMMANDS_TEMPLATE[2]:
            task_pool.append(task)
            task = []
            state = 3
            task.append(3)
        elif arg == COMMANDS_TEMPLATE[3]:
            task_pool.append(task)
            task = []
            state = 4
            task.append(4)
        elif arg == COMMANDS_TEMPLATE[4]:
            task_pool.append(task)
            task = []
            state = 5
            task.append(5)
        else:
            try:
                task.append(float(arg))
                task_pool.append(task)
                task = []
                state = 0
            except Exception:
                state = -1
    elif state == 21:
        task.append(arg)
        task.append(True)
        task_pool.append(task)
        task = []
        state = 0
    elif state == 31:
        try:
            task.append(float(arg))
            state = 32
        except Exception:
            state = -1
    elif state == 32:
        try:
            task.append(float(arg))
            state = 33
        except Exception:
            state = -1
    elif state == 33:
        task.append(arg)
        task_pool.append(task)
        task = []
        state = 0
    elif state == -1:
        break
    elif state == 41:
        if arg == COMMANDS_TEMPLATE[0]:
            task_pool.append(task)
            task = []
            state = 1
            task.append(1)
        elif arg == COMMANDS_TEMPLATE[1]:
            task_pool.append(task)
            task = []
            state = 2
            task.append(2)
        elif arg == COMMANDS_TEMPLATE[2]:
            task_pool.append(task)
            task = []
            state = 3
            task.append(3)
        elif arg == COMMANDS_TEMPLATE[3]:
            task_pool.append(task)
            task = []
            state = 4
            task.append(4)
        elif arg == COMMANDS_TEMPLATE[4]:
            task_pool.append(task)
            task = []
            state = 5
            task.append(5)
        else:
            task.append(arg)
    elif state == 51:
        if arg == COMMANDS_TEMPLATE[0]:
            task_pool.append(task)
            task = []
            state = 1
            task.append(1)
        elif arg == COMMANDS_TEMPLATE[1]:
            task_pool.append(task)
            task = []
            state = 2
            task.append(2)
        elif arg == COMMANDS_TEMPLATE[2]:
            task_pool.append(task)
            task = []
            state = 3
            task.append(3)
        elif arg == COMMANDS_TEMPLATE[3]:
            task_pool.append(task)
            task = []
            state = 4
            task.append(4)
        elif arg == COMMANDS_TEMPLATE[4]:
            task_pool.append(task)
            task = []
            state = 5
            task.append(5)
        else:
            task.append(arg)

if state in [13, 41, 51]:
    task_pool.append(task)
    state = 0

if state != 0 or len(task_pool) == 0:
    show_usage()
    sys.exit()

print("processing started\n", flush=True)
tasks = len(task_pool)

# process data
for i in range(tasks):
    task = task_pool[i]
    number = task[0]
    tsk = task[1:]
    print("\rtask ", i+1, " of ", tasks, ". Type ", number, sep="", end=" ", flush=True)
    if number == 1:
        parameter(tsk)
    elif number == 2:
        activity(tsk)
    elif number == 3:
        graph(tsk)
    elif number == 4:
        bpks(tsk)
    elif number == 5:
        dynamics(tsk)

print("\nscript finished", flush=True)
