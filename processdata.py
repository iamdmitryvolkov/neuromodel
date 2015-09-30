#Network text activity post-processing module (C) Dmitry Volkov 2015

# version 0.1 (20.06.2015)

from imagerender import *
from functionsdrawer import *

data = []
dsize = 0

def addData(text):
	global dsize
	dline = []
	if (dsize > 0):
		for i in text[:dsize]:
			if i == "1":
				dline.append(1)
			else:
				dline.append(0)
		data.append(dline)
	else:
		dsize = len(text)
		addData(text)

def drawActivity(size, name):
	renderImage(data,size,name)

def drawSpikesPerMs(size, name):
	sdata = []
	for i in data:
		sdata.append(sum(i))
	drawSequence(sdata,size,name)

#loading file
dsize = 0
print("opening file data.txt", flush=True)
try:
	file = open("data.txt","rt")
except (FileNotFoundError, IOError):
	print("Error! Creating new file")
	file = open("data.txt", "wt")
	file.write("")
	file.close()
	print("New file created")
for line in file:
	addData(line[:-1])
file.close()
print("data readed successfully", flush=True)

drawActivity(20,"_activity")
drawSpikesPerMs(20,"_spikesPerMs")
print("All operations completed", flush=True)
