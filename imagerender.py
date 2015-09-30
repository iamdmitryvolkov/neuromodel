#Pixel Image Render module. (C) Dmitry Volkov 2015.

#v 0.6 (20.06.2015)

from PIL import Image, ImageDraw

def renderImage(datalist, size, name, horizontal=True):
	if (horizontal):
		sizes = (len(datalist),len(datalist[0]))
	else:
		sizes = (len(datalist[0]),len(datalist))
	img = Image.new("RGB", (sizes[0]*size,sizes[1]*size), (255,255,255))

	draw = ImageDraw.Draw(img)
	
	x = 0
	
	for i in datalist:
		y = 0
		for j in i:
			if j:
				if (horizontal):
					draw.rectangle((x*size, y*size,(x+1)*size,(y+1)*size), (0,0,0))
				else:
					draw.rectangle((y*size, x*size,(y+1)*size,(x+1)*size), (0,0,0))
			y = y + 1
		x = x + 1
	
	img.save(name + ".png", "PNG")
