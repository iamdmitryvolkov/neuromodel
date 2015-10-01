# Network testing data processing module (C) Dmitry Volkov 2015

# version 1.0 (20.07.2015)

import imagerender as ir
import matplotlib.pyplot as plt

#functions

def get_name(number):
    names = ["electrodes current", "neuron membrane resource", "neuron spike", "neuron stability", "neuron u potential", "neuron v potential"]
    if (number == 0):
        return names[0]
    else:
        new_number = number - 1
        neuron_number = int(new_number/5) + 1
        return names[(new_number % 5) + 1] + " " + str(neuron_number)


def load_data(name):
    file = open(name,"tr")
    i = 0
    data = []
    list = []
    electrode_current_list = []
    neuron1_membrane_resource = []
    neuron1_spike_status = []
    neuron1_stability = []
    neuron1_u_potential = []
    neuron1_v_potential = []
    neuron2_membrane_resource = []
    neuron2_spike_status = []
    neuron2_stability = []
    neuron2_u_potential = []
    neuron2_v_potential = []
    neuron3_membrane_resource = []
    neuron3_spike_status = []
    neuron3_stability = []
    neuron3_u_potential = []
    neuron3_v_potential = []
    data.append(list)
    data.append(electrode_current_list)
    data.append(neuron1_membrane_resource)
    data.append(neuron1_spike_status)
    data.append(neuron1_stability)
    data.append(neuron1_u_potential)
    data.append(neuron1_v_potential)
    data.append(neuron2_membrane_resource)
    data.append(neuron2_spike_status)
    data.append(neuron2_stability)
    data.append(neuron2_u_potential)
    data.append(neuron2_v_potential)
    data.append(neuron3_membrane_resource)
    data.append(neuron3_spike_status)
    data.append(neuron3_stability)
    data.append(neuron3_u_potential)
    data.append(neuron3_v_potential)

    for line in file:
        if ( (i % 2) == 0):
            list_item = []
            for j in line.strip().split(", "):
                list_item.append(int(j))
            list.append(list_item)
        else:
            data_list = []
            for j in line.strip().split(", "):
                data_list.append(float(j))
            electrode_current_list.append(data_list[0])
            neuron1_membrane_resource.append(data_list[1])
            neuron1_spike_status.append(data_list[2])
            neuron1_stability.append(data_list[3])
            neuron1_u_potential.append(data_list[4])
            neuron1_v_potential.append(data_list[5])
            neuron2_membrane_resource.append(data_list[6])
            neuron2_spike_status.append(data_list[7])
            neuron2_stability.append(data_list[8])
            neuron2_u_potential.append(data_list[9])
            neuron2_v_potential.append(data_list[10])
            neuron3_membrane_resource.append(data_list[11])
            neuron3_spike_status.append(data_list[12])
            neuron3_stability.append(data_list[13])
            neuron3_u_potential.append(data_list[14])
            neuron3_v_potential.append(data_list[15])
        i = i + 1

    return data

#processing last test
_NUMBER = "3"
_LTFNAME = "Potentials info " + _NUMBER + " [42] data.txt"

data = load_data("testerengine/" + _LTFNAME)

ir.renderImage(data[0] ,2,"testerengine/processed data/" + _NUMBER + "_result")



for i in range(len(data[1:])):
    for j in range(10):
        fig, ax = plt.subplots()
        #fig.add_axes([0, 0, 1, 1])
        #ax.axis('off')
        fig.set_size_inches((200,4))
        plt.plot(data[i+1][2000*j:2000*(j+1)])
        lim = []
        foo = ((i-1) % 5)
        if ((i == 0) or (foo == 0) or (foo == 3) or (foo == 4)):
            for k in range(2000):
                if (i == 0):
                    lim.append(1)
                else:
                    if (foo == 0):
                        lim.append(2)
                    elif (foo == 3):
                        lim.append(7)
                    elif (foo == 4):
                        lim.append(7)
            plt.plot(lim)
        plt.savefig("testerengine/processed data/" + _NUMBER +"_" + get_name(i) + " from " + str(2000*j) +\
                    " to " + str(2000*(j+1))  +'.png', format='png', dpi=100)
        plt.close()