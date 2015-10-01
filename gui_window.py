# gui 2.0 window
# 30.09.2015 Dmitry Volkov

#QT5
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QTabWidget, QMessageBox, QWidget
from PyQt5.QtGui import QIntValidator, QPainter, QColor, QBrush

#GUI
from gui_network_worker import *
from gui_consts import *

#network
from network import *


#window class
class NetworkWindow(QWidget):
			
	#network
	ntw = None
	
	#worker
	worker = None
	
	#Initialization
	def __init__(self):
		super().__init__()
		
		uic.loadUi('form.ui', self)
		self.init_ui()
		
		self.worker = NetworkWorker(self)
		self.ntw = Network(electrodes=9, neuronsPerElectrod=9, electrodeEnteres=4, neuronsEnteres=15, parentGui=self.worker)
		self.show()
		
	
	#Window UI
	def init_ui(self):
		pass
	
	#override
	def closeEvent(self, event):
		self.worker.end_worker()
		
	#Message Box
	def message_box(self, text, title=MESSAGE_TEXT):
		QMessageBox.question(self, title, text, QMessageBox.Ok)
	
