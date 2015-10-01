# Network testing data processing module 2 (C) Dmitry Volkov 2015

# version 1.0 (20.07.2015)

import os
from imagerender import *
import matplotlib.pyplot as plt

def steps_gauss(array, steps):
    if (steps > 1):
        return gauss(steps_gauss(array, steps - 1))
    elif (steps == 1):
        return gauss(array)
    else:
        return None

def gauss(array):
    result = array[:]
    gauss_power = [0.5, 0.3, 0.1]
    length = len(array)
    for i in range(length):
        for j in range(1,4):
            if ((i-j) >= 0):
                result[i-j] = result[i-j] + array[i]*gauss_power[j-1]
            if ((i+j) < length):
                result[i+j] = result[i+j] + array[i]*gauss_power[j-1]
    return result

def load_array(filename):
    file = open("./testerengine/" + filename, "tr")
    list = []
    for line in file:
        list_item = []
        for num in line.strip().split(", "):
            list_item.append(int(num))
        list.append(list_item)
    return list[:1000]

def process(filename):
    arr = load_array(filename)
    renderImage(arr, 2, "./testerengine/old test/" + filename)
    density_function = []
    for i in arr:
        density_function.append(sum(i))
    average = sum(density_function)/len(density_function)
    density_function_gauss = steps_gauss(density_function, 2)
    average_gauss = 0.9 * sum(density_function_gauss)/len(density_function_gauss)
    lim = []
    lim_gauss = []
    pack = []
    packu = []
    packd = []
    for i in range(len(density_function)):
        lim.append(average)
        lim_gauss.append(average_gauss)
        if (density_function_gauss[i] >= average_gauss):
            pack.append(0.9)
        else:
            pack.append(0.1)
        packu.append(1)
        packd.append(0)

    fig, ax = plt.subplots()
    fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    fig.set_size_inches((20,0.6))
    plt.plot(density_function)
    #plt.plot(lim)
    plt.savefig("testerengine/old test/" + filename + "_df.png", format='png', dpi=100)
    plt.close()

    fig, ax = plt.subplots()
    fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    fig.set_size_inches((20,0.6))
    plt.plot(density_function_gauss)
    #plt.plot(lim_gauss)
    plt.savefig("testerengine/old test/" + filename + "_gauss.png", format='png', dpi=100)
    plt.close()

    fig, ax = plt.subplots()
    fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    fig.set_size_inches((20,0.6))
    plt.plot(pack)
    plt.plot(packu)
    plt.plot(packd)
    plt.savefig("testerengine/old test/" + filename + "_packs.png", format='png', dpi=100)
    plt.close()


files = os.listdir("./testerengine/")
target_files = list(filter(lambda x: x.endswith("data.txt") and not x.startswith("Potentials info"), files))

tl = len(target_files)
for i in range(tl):
    print("\rProcessing " + str(i+1) + " of " + str(tl), end="")
    process(target_files[i])
print("\rDone                                         ")
