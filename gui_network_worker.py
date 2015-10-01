# gui 2.0 network working thread
# 30.09.2015 Dmitry Volkov

#QT5
import threading
import time

#GUI
from gui_consts import *

class NetworkWorker(threading.Thread):
		
	parent = None
		
	work = True
	running = False
		
	forceStim = False
	
	def __init__(self, parent):
		self.parent = parent
		threading.Thread.__init__(self,target=self.main_loop)
		self.work = True
		self.start()
		
	def main_loop(self):
		while self.work:
			if self.running:
				if self.parent.ntw != None:
					self.parent.ntw.step()
			else:
				time.sleep(SLEEP_TIME_MAINLOOP)
	
	#stop app
	def end_worker(self):
		self.work = False
	
	#pause work
	def pause(self):
		self.running = False
	
	#start work
	def go(self):
		self.running = True
	
	#flip working
	def flip_running(self):
		self.running = not self.running
	
	#model output callback
	def drawInfo(self, info):
		print(info)
		
			
			
