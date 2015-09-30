#functions draw module (C) Dmitry Volkov 2015

# version 0.7 (20.07.2015)

from imagerender import *

def draw_integer_sequence(data,size,name):
	sz = max(data)
	dat = []
	for i in data:
		sdat = []
		for j in range(sz+1):
			if j == i:
				sdat.append(1)
			else:
				sdat.append(0)
		dat.append(sdat[::-1])
	renderImage(dat,size,name)

def draw_float_sequence(data, size_px, name):
    pass
