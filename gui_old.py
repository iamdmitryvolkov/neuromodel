#QT5 GUI
import sys
import threading
import time

from network import *
from pksmodule import *
from imagerender import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QTabWidget, QMessageBox, QWidget
from PyQt5.QtGui import QIntValidator, QPainter, QColor, QBrush


#Const
WWIDTH = 900
WHEIGHT = 600
UNITS = [["ms","мс"],["s","с"],["min","мин",],["h","ч"],["day","сут"]];
FREQ_PER_GH_CON = [["Frequency: ","Частота: "],["Period: ","Период: "],[" Hz"," Гц"],[" Continuously"," Непрерывно",]]
END_BOX = [["Close","Закрыть"],["Save current network?","Сохранить текущую сеть?"]]
SMALL_SCREEN = ["Sorry, you screen is too small","Извините, ваш экран слишком мал"]
MESSAGEBOX = ["Warning","Внимание"]
POOL_MEMORY = 10000 #10 seconds

#params
langRu = True

#window class
class NetworkWindow(QTabWidget):
	
	class DrawScreen(QtWidgets.QFrame):
		
		pool = None
		cBox = None
		electrodes = 1
		
		def __init__(self, parent, dataPool, cbox):
			super().__init__(parent)
			self.pool = dataPool
			self.cBox = cbox
			
		def paintEvent(self, e):
			qp = QPainter()
			qp.begin(self)
			if (self.cBox.currentIndex()):
				#vertical
				size = int(float(self.width()-4) / self.electrodes)
				qp.drawRect(40,40,size,size)
				pass
			else:
				#horizontal
				size = int(float(self.height()-2) / self.electrodes)
				size = 10
				x = 0
				#print(self.pool.getLast(10))
				for i in self.pool.getLast(45):
					y = 0
					for j in i:
						if j:
							qp.drawRect(20 + 1 + 12*x,20 + 1 + 12*y,size,size)
						y = y + 1
					x = x + 1
			qp.end()
		
		def setElectrodesCount(self,val):
			self.electrodes = val
		
	#network settings dialog window
	class SetNetworkWindow(QWidget):
		
		answer = False
		parentForm = None
		createNew = False
		forceClosing = False
		
		def __init__(self, parent, createnew):
			super().__init__()
			self.parentForm = parent
			self.parentForm.setEnabled(False)
			#fix it
			if self.parentForm.ntw == None:
				noize = (1,3)
			else:
				noize = self.parentForm.ntw.getNoize()
			self.createNew = createnew
			self.setObjectName("SetNetwork")
			self.setFixedSize(245, 180)
			self.move((sw - 245)/2,(sh - 120)/2)
			self.buttons = QtWidgets.QDialogButtonBox(self)
			self.buttons.setGeometry(QtCore.QRect(20, 140, 205, 32))
			self.buttons.setOrientation(QtCore.Qt.Horizontal)
			self.buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
			self.buttons.setObjectName("buttons")
			self.noizeLabel = QtWidgets.QLabel(self)
			self.noizeLabel.setGeometry(QtCore.QRect(20, 83, 60, 15))
			self.noizeLabel.setObjectName("noizeLabel")
			self.noizeTypeBox = QtWidgets.QComboBox(self)
			self.noizeTypeBox.setGeometry(QtCore.QRect(80, 80, 145, 23))
			self.noizeTypeBox.setObjectName("noizeTypeBox")
			self.noizeTypeBox.addItem("")
			self.noizeTypeBox.addItem("")
			self.noizeTypeBox.currentIndexChanged.connect(self.comboBoxSelected)
			self.relativeSlider = QtWidgets.QSlider(self)
			self.relativeSlider.setGeometry(QtCore.QRect(20, 113, 160, 16))
			self.relativeSlider.setOrientation(QtCore.Qt.Horizontal)
			self.relativeSlider.setObjectName("relativeSlider")
			self.relativeSlider.setVisible(False)
			self.relativeSlider.setMaximum(100)
			self.relativeSlider.valueChanged.connect(self.calcLabel)
			self.relativeLabel = QtWidgets.QLabel(self)
			self.relativeLabel.setGeometry(QtCore.QRect(185, 113, 40, 16))
			self.relativeLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
			self.relativeLabel.setObjectName("relativeLabel")
			self.relativeLabel.setVisible(False)
			if noize[0]:
				self.relativeSlider.setValue(noize[1])
			else:
				self.relativeLabel.setText("0%")
			self.spinBox = QtWidgets.QSpinBox(self)
			self.spinBox.setGeometry(QtCore.QRect(20, 110, 205, 24))
			self.spinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
			self.spinBox.setObjectName("spinBox")
			if not noize[0]:
				self.spinBox.setValue(noize[1])
			#self.spinBox.setVisible(False)
			self.electrodeLabel = QtWidgets.QLabel(self)
			self.electrodeLabel.setGeometry(QtCore.QRect(20, 23, 205, 15))
			self.electrodeLabel.setObjectName("electrodeLabel")
			self.electrodeSpinBox = QtWidgets.QSpinBox(self)
			self.electrodeSpinBox.setGeometry(QtCore.QRect(20, 50, 100, 24))
			if (createnew):
				self.electrodeSpinBox.setMinimum(1)
			else:
				self.electrodeSpinBox.setMinimum(self.parentForm.electrodes)
			self.electrodeSpinBox.setMaximum(400)
			self.electrodeSpinBox.setObjectName("electrodeSpinBox")
			self.addElectrodeButton = QtWidgets.QPushButton(self)
			self.addElectrodeButton.setGeometry(QtCore.QRect(125, 50, 100, 23))
			self.addElectrodeButton.setObjectName("addElectrodeButton")
			self.addElectrodeButton.clicked.connect(self.addElectrode)
			
			self.retranslateUi(self)
			self.buttons.accepted.connect(self.accept)
			self.buttons.rejected.connect(self.reject)
			QtCore.QMetaObject.connectSlotsByName(self)
			
			self.noizeTypeBox.setCurrentIndex(noize[0])
			
			self.show()
		
		def comboBoxSelected(self, newid):
			relative = (newid == 1)
			self.spinBox.setVisible(not relative)
			self.relativeLabel.setVisible(relative)
			self.relativeSlider.setVisible(relative)
			if relative:
				self.calcLabel
		
		def addElectrode(self):
			val = self.electrodeSpinBox.value()
			if (val < self.electrodeSpinBox.maximum()):
				self.electrodeSpinBox.setValue(val + 1)
		
		def calcLabel(self):
			self.relativeLabel.setText(str(self.relativeSlider.value()) + "%")
		
		def retranslateUi(self, window):
			_translate = QtCore.QCoreApplication.translate
			if langRu:
				window.setWindowTitle(_translate("SetNetwork", "Настроить"))
				self.noizeLabel.setText(_translate("SetNetwork", "Шум:"))
				self.noizeTypeBox.setItemText(0, _translate("SetNetwork", "Фиксированный"))
				self.noizeTypeBox.setItemText(1, _translate("SetNetwork", "Относительный"))
				self.electrodeLabel.setText(_translate("SetNetwork", "Электроды"))
				self.addElectrodeButton.setText(_translate("SetNetwork", "Добавить"))
			else:
				window.setWindowTitle(_translate("SetNetwork", "Set"))
				self.noizeLabel.setText(_translate("SetNetwork", "Noize:"))
				self.noizeTypeBox.setItemText(0, _translate("SetNetwork", "Fixed"))
				self.noizeTypeBox.setItemText(1, _translate("SetNetwork", "Relative"))
				self.electrodeLabel.setText(_translate("SetNetwork", "Electrodes"))
				self.addElectrodeButton.setText(_translate("SetNetwork", "Add"))
		
		def accept(self):
			self.answer = True
			self.close()
			
		def reject(self):
			self.answer = False
			self.close()
			
		def forceClose(self):
			self.forceClosing = True
			self.close()
		
		def closeEvent(self, event):
			if not self.forceClosing:
				self.parentForm.setEnabled(True)
				if (self.createNew):
					if (self.answer):
						#createGroupDialog
						self.parentForm.groupsData = []
						group = [9,4,15,0, None]
						self.parentForm.groupsData.append(group)
						self.parentForm.pool.clear()
						self.parentForm.ntw = Network(electrodes=self.electrodeSpinBox.value(), neuronsPerElectrod=9, electrodeEnteres=4, neuronsEnteres=15, parentGui=self.parentForm.worker)
				if (self.answer):
					self.parentForm.electrodes = self.electrodeSpinBox.value()
					self.parentForm.setNetworkButton.setEnabled(True)
					b = self.noizeTypeBox.currentIndex()
					if b:
						val = self.relativeSlider.value()
					else:
						val = self.spinBox.value()
					self.parentForm.ntw.setNoize(b,val)
					ilist = self.parentForm.electrodesList
					if (ilist.count() > self.electrodeSpinBox.value()):
						while(ilist.count() > self.electrodeSpinBox.value()):
							ilist.takeItem(self.electrodeSpinBox.value())
					else:
						while(ilist.count() < self.electrodeSpinBox.value()):
							ilist.addItem(str(ilist.count()+1))
					self.parentForm.drawingField.setElectrodesCount(self.electrodeSpinBox.value())
	
	#save activity part dialog window
	class SaveInfo(QWidget):
		
		TIMES = [10,20,50,100,150,200,300,400,500,750,1000,1250,1500,2000,3000,4000,5000,6000,7000,8000,9000,10000]
		answer = False
		parentForm = None
		forceClosing = False
		recordedTime = 0
		
		def __init__(self, parent):
			super().__init__()
			self.parentForm = parent
			self.parentForm.setEnabled(False)
			self.recordedTime = self.parentForm.pool.getLength()
			self.setObjectName("saveinfo")
			self.setFixedSize(200, 180)
			self.move((sw - 200)/2,(sh - 180)/2)
			self.saveLabel = QtWidgets.QLabel(self)
			self.saveLabel.setGeometry(QtCore.QRect(20, 20, 160, 15))
			self.saveLabel.setObjectName("saveLabel")
			self.saveButton = QtWidgets.QPushButton(self)
			self.saveButton.setGeometry(QtCore.QRect(20, 140, 160, 23))
			self.saveButton.setObjectName("saveButton")
			self.saveButton.clicked.connect(self.saveButtonPressed)
			self.saveTypeBox = QtWidgets.QComboBox(self)
			self.saveTypeBox.setGeometry(QtCore.QRect(20, 110, 160, 23))
			self.saveTypeBox.setObjectName("saveTypeBox")
			self.saveTypeBox.addItem("")
			self.saveTypeBox.addItem("")
			self.saveTypeBox.addItem("")
			self.saveTypeBox.addItem("")
			self.saveTypeBox.currentIndexChanged.connect(self.changeIndex)
			self.saveTimeSlider = QtWidgets.QSlider(self)
			self.saveTimeSlider.setGeometry(QtCore.QRect(20, 50, 160, 16))
			self.saveTimeSlider.setMinimum(0)
			self.saveTimeSlider.setMaximum(21)
			self.saveTimeSlider.setOrientation(QtCore.Qt.Horizontal)
			self.saveTimeSlider.setObjectName("saveTimeSlider")
			self.saveTimeSlider.valueChanged.connect(self.sliderMove)
			self.label = QtWidgets.QLabel(self)
			self.label.setGeometry(QtCore.QRect(20, 80, 160, 15))
			self.label.setAlignment(QtCore.Qt.AlignCenter)
			self.label.setObjectName("label")
			
			self.retranslateUi(self)
			QtCore.QMetaObject.connectSlotsByName(self)
			self.setMaxTime(2000)
			self.show()
			
		def retranslateUi(self, window):
			_translate = QtCore.QCoreApplication.translate
			if langRu:
				self.setWindowTitle(_translate("saveinfo", "Сохранение"))
				self.saveLabel.setText(_translate("saveinfo", "Сохранить последние"))
				self.saveButton.setText(_translate("saveinfo", "Сохранить"))
				self.saveTypeBox.setItemText(0, _translate("saveinfo", "Изображение. Мелко"))
				self.saveTypeBox.setItemText(1, _translate("saveinfo", "Изображение"))
				self.saveTypeBox.setItemText(2, _translate("saveinfo", "Текст"))
				self.saveTypeBox.setItemText(3, _translate("saveinfo", "Пачки"))
			else:
				self.setWindowTitle(_translate("saveinfo", "Saving"))
				self.saveLabel.setText(_translate("saveinfo", "Save last.."))
				self.saveButton.setText(_translate("saveinfo", "Save"))
				self.saveTypeBox.setItemText(0, _translate("saveinfo", "Image. Small"))
				self.saveTypeBox.setItemText(1, _translate("saveinfo", "Image"))
				self.saveTypeBox.setItemText(2, _translate("saveinfo", "Text"))
				self.saveTypeBox.setItemText(3, _translate("saveinfo", "Packs"))
				
			self.label.setText(_translate("saveinfo", "10 " + UNITS[0][langRu]))
		
		def saveButtonPressed(self):
			self.answer = True
			self.close()
		
		def changeIndex(self, val):
			if (val==0):
				self.setMaxTime(2000)
			elif (val==1):
				self.setMaxTime(1000)
			else:
				self.setMaxTime(10000)
		
		def setMaxTime(self, time):
			m = min(self.recordedTime,time)
			i = 0
			while((i < 22) and (self.TIMES[i]<=m)):
				i = i + 1
			self.saveTimeSlider.setMaximum(i-1)
			
		def sliderMove(self, val):
			sel = self.TIMES[val]
			if (sel < 1000):
				tsel = str(sel) + " " + UNITS[0][langRu]
			else:
				tsel = str(float(sel)/1000) + " " + UNITS[1][langRu]
			self.label.setText(tsel)
		
		def forceClose(self):
			self.forceClosing = True
			self.close()
		
		def closeEvent(self, event):
			if not self.forceClosing:
				self.parentForm.setEnabled(True)
				if (self.saveTypeBox.currentIndex() == 0):
					self.saveImage(True)
				elif(self.saveTypeBox.currentIndex() == 1):
					self.saveImage(False)
				elif(self.saveTypeBox.currentIndex() == 2):
					self.saveText()
				else:
					self.savePacks()
					
		def saveImage(self, small):
			if small:
				size = 1
			else:
				size = 2
			renderImage(self.parentForm.pool.getLast(self.TIMES[self.saveTimeSlider.value()]), size, "Activity")
			
		def saveText(self):
			pass
			
		def savePacks(self):
			pass
	
	#real time saving activity dialog window
	class SavingActivity(QWidget):
		
		answer = False
		parentForm = None
		forceClosing = False
		
		def __init__(self, parent):
			super().__init__()
			self.parentForm = parent
			self.parentForm.setEnabled(False)
			self.setObjectName("SavingActivity")
			self.setFixedSize(140, 120)
			self.move((sw - 140)/2,(sh - 120)/2)
			self.textCheck = QtWidgets.QCheckBox(self)
			self.textCheck.setGeometry(QtCore.QRect(20, 20, 100, 21))
			self.textCheck.setObjectName("textCheck")
			self.packsCheck = QtWidgets.QCheckBox(self)
			self.packsCheck.setGeometry(QtCore.QRect(20, 50, 100, 21))
			self.packsCheck.setObjectName("packsCheck")
			self.okButton = QtWidgets.QPushButton(self)
			self.okButton.setGeometry(QtCore.QRect(20, 80, 100, 23))
			self.okButton.setObjectName("okButton")
			self.okButton.clicked.connect(self.okButtonPressed)
			
			self.retranslateUi(self)
			QtCore.QMetaObject.connectSlotsByName(self)
			
			self.show()
			
		def retranslateUi(self, window):
			_translate = QtCore.QCoreApplication.translate
			if langRu:
				self.setWindowTitle(_translate("saveinfo", "Сохранение"))
				self.textCheck.setText(_translate("SavingActivity", "Текст"))
				self.packsCheck.setText(_translate("SavingActivity", "Пачки"))
				self.okButton.setText(_translate("SavingActivity", "ОК"))
			else:
				self.setWindowTitle(_translate("saveinfo", "Saving"))
				self.textCheck.setText(_translate("SavingActivity", "Text"))
				self.packsCheck.setText(_translate("SavingActivity", "Packs"))
				self.okButton.setText(_translate("SavingActivity", "OK"))
		
		def okButtonPressed(self):
			self.answer = True
			self.close()
		
		def forceClose(self):
			self.forceClosing = True
			self.close()
		
		def closeEvent(self, event):
			if not self.forceClosing:
				self.parentForm.setEnabled(True)
				print(self.answer)
				
	class DataPool():
		#dataList
		index = 0
		dataList = None
		
		def __init__(self):
			self.dataList = []
		
		def clear(self):
			self.dataList = []
		
		def add(self, data):
			if (len(self.dataList) < POOL_MEMORY):
				self.dataList.append(data)
				self.index = self.index + 1
			else:
				if (self.index < POOL_MEMORY):
					self.dataList[self.index] = data
					self.index = self.index + 1
				else:
					self.dataList[0] = data
					self.index = 1
		
		def getLength(self):
			return len(self.dataList)
		
		def getData(self):
			return self.dataList[self.index:]+self.dataList[:self.index]
			
		def getLast(self, leng):
			return self.getData()[-leng:]
	
	class NetworkWorker(threading.Thread):
		
		parent = None
		
		work = True
		running = False
		
		forceStim = False
	
		def __init__(self, parent):
			self.parent = parent
			threading.Thread.__init__(self,target=self.mainLoop)
			self.work = True
			self.start()
		
		def mainLoop(self):
			while self.work:
				if self.running:
					#networkExistTest
					if (self.parent.electrodes != None):
						if (len(self.parent.groupsData) == 0):
							#warning Group is not created!!!
							self.pause()
						else:
							#stimulator
							if (self.forceStim):
								self.stimNeurs()
								self.parent.stepsToStimulation = self.parent.period
								self.forceStim = False
							else:
								if (self.parent.stimulationEnabler.isChecked()):
									if (self.parent.stepsToStimulation <= 0):
										self.stimNeurs()
										self.parent.stepsToStimulation = self.parent.period
									else:
										self.parent.stepsToStimulation = self.parent.stepsToStimulation - 1
					
							#step
							self.parent.ntw.step()
					
							#auto stop
							if (self.parent.endLabel.isChecked()):
								if (self.parent.stepsToStop > 0):
									self.parent.stepsToStop = self.parent.stepsToStop - 1
								else:
									self.pause()
							self.parent.drawStopTime()
							self.parent.drawingField.update()
					else:
						#warning Network is not created!!!
						self.pause()
				else:
					time.sleep(0.75)
			
		def endWorker(self):
			self.work = False
			
		def pause(self):
			self.running = False
		
		def flipRunning(self):
			self.running = not self.running
			
		def drawInfo(self, info):
			self.parent.pool.add(info)
		
		def stimNow(self):
			self.forceStim = True
			
		def stimNeurs(self):
			l = []
			ilist = self.parent.electrodesList
			for i in range(ilist.count()):
				if ilist.item(i).isSelected():
					l.append(i)
			self.parent.ntw.stimulate(l)
			
	#network
	ntw = None
	
	electrodes = None
	groupsData = []
	#DataItem[neurs per electrode, electrode enteres, electrode enteres in group, electrode eneteres out group, neuron params]
	#neuronParamsItem =[]
	
	#worker
	worker = None
	#dialog
	dialogWindow = None
	#pool
	pool = DataPool()
	
	#tab1
	#stoptimer
	freeChanging = False
	stepsToStop = 0
	writeTimer = None
	#frequency
	period = 0
	stepsToStimulation = 0
	
	#tab2
	
	#Initialization
	def __init__(self, sw, sh):
		super().__init__()
		
		self.initUI(sw, sh)
		
		self.worker = self.NetworkWorker(self)
		#self.ntw = Network(electrodes=9, neuronsPerElectrod=9, electrodeEnteres=4, neuronsEnteres=15, parentGui=self.worker)
		#NewLoadSkipDialog
		self.show()
		
		#not yet
		self.loadNetworkButton.setEnabled(False)
		self.fieldOrientationBox.setEnabled(False)
		self.programStimulationButton.setEnabled(False)
		self.programStimulationEdit.setEnabled(False)
		self.programLabel.setEnabled(False)
		self.saveAllButton.setEnabled(False)
		self.saveButton.setEnabled(False)
		self.setGroupsButton.setEnabled(False)
		#self.saveNetworkButton.setEnabled(True)
		
	
	#Window UI
	def initUI(self, sw, sh):
		self.setFixedSize(WWIDTH,WHEIGHT)
		self.move((sw - WWIDTH)/2,(sh - WHEIGHT)/2)
		self.setObjectName("MainWindow")
		#tab 1
		self.tab_work = QtWidgets.QWidget()
		self.tab_work.setObjectName("tab_work")
		self.fieldButtons = QtWidgets.QWidget(self.tab_work)
		self.fieldButtons.setGeometry(QtCore.QRect(5, 343, 590, 27))
		self.fieldButtons.setObjectName("fieldButtons")
		self.layoutWidget = QtWidgets.QWidget(self.fieldButtons)
		self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 590, 27))
		self.layoutWidget.setObjectName("layoutWidget")
		self.horizontalFieldLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
		self.horizontalFieldLayout.setContentsMargins(0, 0, 0, 0)
		self.horizontalFieldLayout.setObjectName("horizontalFieldLayout")
		spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
		self.horizontalFieldLayout.addItem(spacerItem)
		self.fieldOrientationBox = QtWidgets.QComboBox(self.layoutWidget)
		self.fieldOrientationBox.setObjectName("fieldOrientationBox")
		self.fieldOrientationBox.addItem("")
		self.fieldOrientationBox.addItem("")
		self.fieldOrientationBox.currentIndexChanged.connect(self.orientationBoxChanged)
		self.horizontalFieldLayout.addWidget(self.fieldOrientationBox)
		self.saveAllButton = QtWidgets.QCheckBox(self.layoutWidget)
		self.saveAllButton.setObjectName("saveAllButton")
		self.horizontalFieldLayout.addWidget(self.saveAllButton)
		self.saveButton = QtWidgets.QPushButton(self.layoutWidget)
		self.saveButton.setObjectName("saveButton")
		self.saveButton.clicked.connect(self.saveDialog)
		self.horizontalFieldLayout.addWidget(self.saveButton)
		self.periodLabel = QtWidgets.QLabel(self.tab_work)
		self.periodLabel.setGeometry(QtCore.QRect(245, 440, 185, 15))
		self.periodLabel.setObjectName("periodLabel")
		self.frequencyLabel = QtWidgets.QLabel(self.tab_work)
		self.frequencyLabel.setGeometry(QtCore.QRect(245, 410, 185, 15))
		self.frequencyLabel.setObjectName("frequencyLabel")
		self.stimulationEnabler = QtWidgets.QCheckBox(self.tab_work)
		self.stimulationEnabler.setGeometry(QtCore.QRect(245, 500, 185, 21))
		self.stimulationEnabler.setObjectName("stimulationEnabler")
		self.periodSlider = QtWidgets.QSlider(self.tab_work)
		self.periodSlider.setGeometry(QtCore.QRect(245, 470, 185, 16))
		self.periodSlider.setMaximum(100)
		self.periodSlider.setProperty("value", 100)
		self.periodSlider.setOrientation(QtCore.Qt.Horizontal)
		self.periodSlider.setObjectName("periodSlider")
		self.periodSlider.valueChanged.connect(self.periodChange)
		self.electrodeAllButton = QtWidgets.QPushButton(self.tab_work)
		self.electrodeAllButton.setGeometry(QtCore.QRect(10, 543, 97, 23))
		self.electrodeAllButton.setObjectName("electrodeAllButton")
		self.electrodeAllButton.clicked.connect(self.checkAllElectrodes)
		self.electrodeNullButton = QtWidgets.QPushButton(self.tab_work)
		self.electrodeNullButton.setGeometry(QtCore.QRect(117, 543, 97, 23))
		self.electrodeNullButton.setObjectName("electodeNullButton")
		self.electrodeNullButton.clicked.connect(self.unCheckAllElectrodes)
		self.electrodesLabel = QtWidgets.QLabel(self.tab_work)
		self.electrodesLabel.setGeometry(QtCore.QRect(10, 380, 205, 15))
		self.electrodesLabel.setObjectName("electrodesLabel")
		self.electrodesList = QtWidgets.QListWidget(self.tab_work)
		self.electrodesList.setGeometry(QtCore.QRect(10, 400, 205, 137))
		self.electrodesList.setObjectName("electrodesList")
		self.electrodesList.setSelectionMode(0x0002)
		self.programLabel = QtWidgets.QLabel(self.tab_work)
		self.programLabel.setGeometry(QtCore.QRect(450, 380, 181, 16))
		self.programLabel.setObjectName("programLabel")
		self.programStimulationEdit = QtWidgets.QPlainTextEdit(self.tab_work)
		self.programStimulationEdit.setGeometry(QtCore.QRect(450, 400, 437, 137))
		self.programStimulationEdit.setObjectName("programStimulationEdit")
		self.programStimulationButton = QtWidgets.QPushButton(self.tab_work)
		self.programStimulationButton.setGeometry(QtCore.QRect(777, 543, 110, 23))
		self.programStimulationButton.setObjectName("programStmulationButton")
		self.plus100 = QtWidgets.QPushButton(self.tab_work)
		self.plus100.setGeometry(QtCore.QRect(710, 185, 80, 23))
		self.plus100.setObjectName("plus100")
		self.plus100.clicked.connect(self.addStopTime100)
		self.startPauseButton = QtWidgets.QPushButton(self.tab_work)
		self.startPauseButton.setGeometry(QtCore.QRect(620, 215, 170, 23))
		self.startPauseButton.setObjectName("startPauseButon")
		self.startPauseButton.clicked.connect(self.startPauseButtonPressed)
		self.plus10 = QtWidgets.QPushButton(self.tab_work)
		self.plus10.setGeometry(QtCore.QRect(800, 185, 80, 23))
		self.plus10.setObjectName("plus10")
		self.plus10.clicked.connect(self.addStopTime10)
		self.plus1 = QtWidgets.QPushButton(self.tab_work)
		self.plus1.setGeometry(QtCore.QRect(800, 215, 80, 23))
		self.plus1.setObjectName("plus1")
		self.plus1.clicked.connect(self.addStopTime1)
		self.plus1000 = QtWidgets.QPushButton(self.tab_work)
		self.plus1000.setGeometry(QtCore.QRect(620, 185, 80, 23))
		self.plus1000.setObjectName("plus1000")
		self.plus1000.clicked.connect(self.addStopTime1000)
		self.endLabel = QtWidgets.QCheckBox(self.tab_work)
		self.endLabel.setGeometry(QtCore.QRect(620, 125, 211, 21))
		self.endLabel.setObjectName("endLabel")
		self.timeBox = QtWidgets.QComboBox(self.tab_work)
		self.timeBox.setGeometry(QtCore.QRect(830, 155, 50, 23))
		self.timeBox.setObjectName("timeBox")
		self.timeBox.addItem("")
		self.timeBox.addItem("")
		self.timeBox.addItem("")
		self.timeBox.addItem("")
		self.timeBox.currentIndexChanged.connect(self.changeTimeIndex)
		self.timerEdit = QtWidgets.QLineEdit(self.tab_work)
		self.timerEdit.setGeometry(QtCore.QRect(620, 155, 200, 23))
		self.timerEdit.setValidator(QIntValidator(0, 10000, self.timerEdit))
		self.timerEdit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
		self.timerEdit.setObjectName("timerEdit")
		self.timerEdit.setText("0.0")
		self.timerEdit.textChanged.connect(self.changeTimerText)
		#self.drawingField = QtWidgets.QFrame(self.tab_work)
		self.drawingField = self.DrawScreen(self.tab_work, self.pool, self.fieldOrientationBox)
		self.drawingField.setGeometry(QtCore.QRect(5, 5, 590, 333))
		self.drawingField.setAutoFillBackground(True)
		self.drawingField.setFrameShape(QtWidgets.QFrame.StyledPanel)
		self.drawingField.setFrameShadow(QtWidgets.QFrame.Raised)
		self.drawingField.setObjectName("drawingField")
		self.stimNowButton = QtWidgets.QPushButton(self.tab_work)
		self.stimNowButton.setGeometry(QtCore.QRect(245, 530, 185, 23))
		self.stimNowButton.setObjectName("stimNowButton")
		self.stimNowButton.clicked.connect(self.stimNowPressed)
		self.addTab(self.tab_work, "")
		#tab 2
		self.tab_study = QtWidgets.QWidget()
		self.tab_study.setObjectName("tab_study")
		self.groupList = QtWidgets.QListView(self.tab_study)
		self.groupList.setGeometry(QtCore.QRect(20, 40, 260, 420))
		self.groupList.setObjectName("groupList")
		self.setGroupsButton = QtWidgets.QPushButton(self.tab_study)
		self.setGroupsButton.setGeometry(QtCore.QRect(20, 470, 260, 23))
		self.setGroupsButton.setObjectName("setGroupsButton")
		self.connectionsAddButton = QtWidgets.QPushButton(self.tab_study)
		self.connectionsAddButton.setGeometry(QtCore.QRect(20, 500, 260, 23))
		self.connectionsAddButton.setObjectName("connectionsAddButton")
		self.groupLabel = QtWidgets.QLabel(self.tab_study)
		self.groupLabel.setGeometry(QtCore.QRect(20, 20, 59, 15))
		self.groupLabel.setObjectName("groupLabel")
		self.addGroupButton = QtWidgets.QPushButton(self.tab_study)
		self.addGroupButton.setGeometry(QtCore.QRect(20, 530, 125, 23))
		self.addGroupButton.setObjectName("addGroupButton")
		self.learnLabel = QtWidgets.QLabel(self.tab_study)
		self.learnLabel.setGeometry(QtCore.QRect(320, 20, 261, 16))
		self.learnLabel.setObjectName("learnLabel")
		self.learnSteps = QtWidgets.QSpinBox(self.tab_study)
		self.learnSteps.setGeometry(QtCore.QRect(390, 530, 41, 24))
		self.learnSteps.setObjectName("learnSteps")
		self.learnStart = QtWidgets.QPushButton(self.tab_study)
		self.learnStart.setGeometry(QtCore.QRect(440, 530, 121, 23))
		self.learnStart.setObjectName("learnStart")
		self.learnProgramEdit = QtWidgets.QTextEdit(self.tab_study)
		self.learnProgramEdit.setGeometry(QtCore.QRect(320, 40, 260, 480))
		self.learnProgramEdit.setObjectName("learnProgramEdit")
		self.stepsLabel = QtWidgets.QLabel(self.tab_study)
		self.stepsLabel.setGeometry(QtCore.QRect(340, 535, 59, 15))
		self.stepsLabel.setObjectName("stepsLabel")
		self.mainBox = QtWidgets.QGroupBox(self.tab_study)
		self.mainBox.setGeometry(QtCore.QRect(620, 20, 260, 171))
		self.mainBox.setObjectName("mainBox")
		self.newNetworkButton = QtWidgets.QPushButton(self.mainBox)
		self.newNetworkButton.setGeometry(QtCore.QRect(20, 40, 220, 23))
		self.newNetworkButton.setObjectName("newNetworkButton")
		self.newNetworkButton.clicked.connect(self.networkNew)
		self.saveNetworkButton = QtWidgets.QPushButton(self.mainBox)
		self.saveNetworkButton.setGeometry(QtCore.QRect(20, 70, 220, 23))
		self.saveNetworkButton.setObjectName("saveNetworkButton")
		self.saveNetworkButton.clicked.connect(self.networkSave)
		self.saveNetworkButton.setEnabled(False)
		self.loadNetworkButton = QtWidgets.QPushButton(self.mainBox)
		self.loadNetworkButton.setGeometry(QtCore.QRect(20, 100, 220, 23))
		self.loadNetworkButton.setObjectName("loadNetworkButton")
		self.loadNetworkButton.clicked.connect(self.networkLoad)
		self.setNetworkButton = QtWidgets.QPushButton(self.mainBox)
		self.setNetworkButton.setGeometry(QtCore.QRect(20, 130, 220, 23))
		self.setNetworkButton.setObjectName("setNetworkButton")
		self.setNetworkButton.clicked.connect(self.networkSet)
		self.setNetworkButton.setEnabled(False)
		self.delGroupButton = QtWidgets.QPushButton(self.tab_study)
		self.delGroupButton.setGeometry(QtCore.QRect(155, 530, 125, 23))
		self.delGroupButton.setObjectName("delGroupButton")
		self.packsList = QtWidgets.QListView(self.tab_study)
		self.packsList.setGeometry(QtCore.QRect(620, 230, 260, 290))
		self.packsList.setObjectName("packsList")
		self.packsLabel = QtWidgets.QLabel(self.tab_study)
		self.packsLabel.setGeometry(QtCore.QRect(620, 210, 59, 15))
		self.packsLabel.setObjectName("packsLabel")
		self.addPackButton = QtWidgets.QPushButton(self.tab_study)
		self.addPackButton.setGeometry(QtCore.QRect(620, 530, 125, 23))
		self.addPackButton.setObjectName("addPackButton")
		self.delPackButton = QtWidgets.QPushButton(self.tab_study)
		self.delPackButton.setGeometry(QtCore.QRect(755, 530, 125, 23))
		self.delPackButton.setObjectName("delPackButton")
		self.addTab(self.tab_study, "")
		#tab 3
		self.tab_help = QtWidgets.QWidget()
		self.tab_help.setObjectName("tab_help")
		self.label = QtWidgets.QLabel(self.tab_help)
		self.label.setGeometry(QtCore.QRect(210, 140, 471, 261))
		self.label.setObjectName("label")
		#self.addTab(self.tab_help, "")
		
		QtCore.QMetaObject.connectSlotsByName(self)
		self.retranslateUI(langRu)
		self.writeTimer = threading.Timer(0.75, self.drawStopTime)
		
	def retranslateUI(self, ru):
		_translate = QtCore.QCoreApplication.translate
		if ru:
			self.setWindowTitle(_translate("MainWindow", "Network"))
			
			self.setTabText(self.indexOf(self.tab_work), _translate("MainWindow", "Работа сети"))
			self.fieldOrientationBox.setItemText(0, _translate("MainWindow", "Горизонтально"))
			self.fieldOrientationBox.setItemText(1, _translate("MainWindow", "Вертикально"))
			self.saveAllButton.setText(_translate("MainWindow", "Сохранять вывод"))
			self.saveButton.setText(_translate("MainWindow", "Сохранить кусок вывода"))
			self.endLabel.setText(_translate("MainWindow", "Остановить через"))
			#to spec_block
			self.startPauseButton.setText(_translate("MainWindow", "Старт / Пауза"))
			self.electrodesLabel.setText(_translate("MainWindow", "Электроды"))
			self.electrodeAllButton.setText(_translate("MainWindow", "Отметить все"))
			self.electrodeNullButton.setText(_translate("MainWindow", "Снять все"))
			self.stimulationEnabler.setText(_translate("MainWindow", "Включить стимуляцию"))
			self.stimNowButton.setText("Стимулировать сейчас")
			self.programLabel.setText(_translate("MainWindow", "Стимуляция по программе"))
			self.programStimulationButton.setText(_translate("MainWindow", "Стимулировать"))
			
			self.setTabText(self.indexOf(self.tab_study), _translate("MainWindow", "Обучение сети"))
			self.groupLabel.setText(_translate("MainWindow", "Группы"))
			self.addGroupButton.setText(_translate("MainWindow", "Добавить"))
			self.setGroupsButton.setText(_translate("MainWindow", "Настроить группы"))
			self.connectionsAddButton.setText(_translate("MainWindow", "Добавить связи"))
			self.learnLabel.setText(_translate("MainWindow", "Программа обучения"))
			self.learnStart.setText(_translate("MainWindow", "Обучить"))
			self.stepsLabel.setText(_translate("MainWindow", "Шаги"))
			self.mainBox.setTitle(_translate("MainWindow", "Сеть"))
			self.newNetworkButton.setText(_translate("MainWindow", "Новая"))
			self.saveNetworkButton.setText(_translate("MainWindow", "Сохранить"))
			self.loadNetworkButton.setText(_translate("MainWindow", "Загрузить"))
			self.setNetworkButton.setText(_translate("MainWindow", "Настроить"))
			self.delGroupButton.setText(_translate("MainWindow", "Удалить"))
			self.packsLabel.setText(_translate("MainWindow", "Пачки"))
			self.addPackButton.setText(_translate("MainWindow", "Добавить"))
			self.delPackButton.setText(_translate("MainWindow", "Удалить"))
			
			self.setTabText(self.indexOf(self.tab_help), _translate("MainWindow", "Помощь"))
			self.label.setText(_translate("MainWindow", "<html><head/><body><p>Здесь могла бы быть ваша реклама...</p><p><br/></p><p>..Ну или хотя бы помощь.</p><p><br/></p><p>Хотя может в финальной версии она и не появится</p><p><br/></p><p>Have a nice day =)</p></body></html>"))
		else:
			self.setWindowTitle(_translate("MainWindow", "Network"))
			
			self.setTabText(self.indexOf(self.tab_work), _translate("MainWindow", "Work"))
			self.fieldOrientationBox.setItemText(0, _translate("MainWindow", "Horizontal"))
			self.fieldOrientationBox.setItemText(1, _translate("MainWindow", "Vertical"))
			self.saveAllButton.setText(_translate("MainWindow", "Save output"))
			self.saveButton.setText(_translate("MainWindow", "Save output's part"))
			self.endLabel.setText(_translate("MainWindow", "Stop after"))
			#spec_block
			self.startPauseButton.setText(_translate("MainWindow", "Start / Pause"))
			self.electrodesLabel.setText(_translate("MainWindow", "Electrodes"))
			self.electrodeAllButton.setText(_translate("MainWindow", "Check all"))
			self.electrodeNullButton.setText(_translate("MainWindow", "Uncheck all"))
			self.stimulationEnabler.setText(_translate("MainWindow", "Enable stimulation"))
			self.stimNowButton.setText("Stimulate now")
			self.programLabel.setText(_translate("MainWindow", "Stimulation by algorithm"))
			self.programStimulationButton.setText(_translate("MainWindow", "Stimulate"))
			
			self.setTabText(self.indexOf(self.tab_study), _translate("MainWindow", "Learning"))
			self.groupLabel.setText(_translate("MainWindow", "Groups"))
			self.addGroupButton.setText(_translate("MainWindow", "Add"))
			self.setGroupsButton.setText(_translate("MainWindow", "Set groups"))
			self.connectionsAddButton.setText(_translate("MainWindow", "Add connections"))
			self.learnLabel.setText(_translate("MainWindow", "Learning algorithm"))
			self.learnStart.setText(_translate("MainWindow", "Learn"))
			self.stepsLabel.setText(_translate("MainWindow", "Steps"))
			self.mainBox.setTitle(_translate("MainWindow", "Network"))
			self.newNetworkButton.setText(_translate("MainWindow", "New"))
			self.saveNetworkButton.setText(_translate("MainWindow", "Save"))
			self.loadNetworkButton.setText(_translate("MainWindow", "Load"))
			self.setNetworkButton.setText(_translate("MainWindow", "Set"))
			self.delGroupButton.setText(_translate("MainWindow", "Delete"))
			self.packsLabel.setText(_translate("MainWindow", "Packs"))
			self.addPackButton.setText(_translate("MainWindow", "Add"))
			self.delPackButton.setText(_translate("MainWindow", "Delete"))
			
			self.setTabText(self.indexOf(self.tab_help), _translate("MainWindow", "Help"))
			self.label.setText(_translate("MainWindow", "<html><head/><body><p>You ads may be here...</p><p><br/></p><p>..Or even help.</p><p><br/></p><p>Maybe in final version there will be nothing</p><p><br/></p><p>Have a nice day =)</p></body></html>"))
		
		self.timeBox.setItemText(0, _translate("MainWindow", UNITS[0][ru]))
		self.timeBox.setItemText(1, _translate("MainWindow", UNITS[1][ru]))
		self.timeBox.setItemText(2, _translate("MainWindow", UNITS[2][ru]))
		self.timeBox.setItemText(3, _translate("MainWindow", UNITS[3][ru]))
		self.renameButtonsUnits(0, ru)
		self.recalculateFreqlabels(ru)
	
	def checkAllElectrodes(self):
		ilist = self.electrodesList
		for i in range(ilist.count()):
			ilist.item(i).setSelected(True)
			
	def unCheckAllElectrodes(self):
		ilist = self.electrodesList
		for i in range(ilist.count()):
			ilist.item(i).setSelected(False)
	
	#override
	def closeEvent(self, event):
		self.worker.endWorker()
		if (self.dialogWindow != None):
			self.dialogWindow.forceClose()
		#reply = QtWidgets.QMessageBox().question(self, END_BOX[0][langRu], END_BOX[1][langRu], QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
		
		#if reply == QtWidgets.QMessageBox.Save:
			#event.accept()
			#save
		#elif(reply == QtWidgets.QMessageBox.Discard):
			#event.accept()
		#else:
			#event.ignore()
	
	def addGroup(self):
		pass
	
	def selectGroupParams(self):
		pass
	
	def messageB(self, text):
		QMessageBox.question(self, MESSAGEBOX[langRu], text[langRu], QMessageBox.Ok)
	
	def saveDialog(self):
		if (self.pool.getLength() >= 10):
			self.dialogWindow = self.SaveInfo(self)
		else:
			self.messageB(["Network hasn't been worked 10 ms yet", "Сеть еще не проработала 10 мс"])
			
	def stimNowPressed(self):
		self.worker.stimNow()
	
	
	#network control console
	def networkNew(self):
		self.worker.pause()
		self.dialogWindow = self.SetNetworkWindow(self, True)
	
	def networkSave(self):
		pass
		self.dialogWindow = self.SavingActivity(self)
		
	def networkLoad(self):
		self.dialogWindow = self.SaveInfo(self)
		
		
	def networkSet(self):
		self.worker.pause()
		self.dialogWindow = self.SetNetworkWindow(self, False)
	
	def startPauseButtonPressed(self):
		if ((self.endLabel.isChecked()) and (self.stepsToStop <= 0)):
			self.endLabel.setChecked(False)
		self.worker.flipRunning()
		
	def recalculateFreqlabels(self, ru):
		if (self.period == 0):
			self.frequencyLabel.setText(FREQ_PER_GH_CON[0][ru] + FREQ_PER_GH_CON[3][ru])
		else:
			self.frequencyLabel.setText(FREQ_PER_GH_CON[0][ru] + str(float(int(100000/(self.period + 1)))/100) + FREQ_PER_GH_CON[2][ru])
		self.periodLabel.setText(FREQ_PER_GH_CON[1][ru] + str(self.period) + " " + UNITS[0][ru])
	
	def renameButtonsUnits(self, number, ru):
		self.plus1000.setText("+1 " + UNITS[number + 1][ru])
		self.plus100.setText("+100 " + UNITS[number][ru])
		self.plus10.setText("+10 " + UNITS[number][ru])
		self.plus1.setText("+1 " + UNITS[number][ru])
	
	def orientationBoxChanged(self):
		self.drawingField.update()
	
	def periodChange(self, val):
		self.period = 100 - val
		self.stepsToStimulation = self.period
		self.recalculateFreqlabels(langRu)
	
	def addStopTime1(self):
		self.addStopTime(1, False)
	
	def addStopTime10(self):
		self.addStopTime(10, False)
	
	def addStopTime100(self):
		self.addStopTime(100, False)
		
	def addStopTime1000(self):
		self.addStopTime(1, True)
		
	
	def changeTimerText(self):
		if not self.freeChanging:
			mult = 1
			index = self.timeBox.currentIndex()
			if (index == 0):
				mult = 1
			elif (index == 1):
				mult = 1000
			elif (index == 2):
				mult = 60000
			elif (index == 3):
				mult = 3600000
			try:
				val = float(self.timerEdit.text())
			except Exception:
				val = 0
			self.stepsToStop = int(mult*val)
			self.writeTimer.cancel()
			self.writeTimer = threading.Timer(0.75, self.drawStopTime)
			self.writeTimer.start() 
			
			
	def drawStopTime(self):
		self.freeChanging = True
		index = self.timeBox.currentIndex()
		if (index == 0):
			self.timerEdit.setText(str(self.stepsToStop))
		elif (index == 1):
			self.timerEdit.setText(str(float(self.stepsToStop)/1000))
		elif (index == 2):
			self.timerEdit.setText(str(float(self.stepsToStop)/60000))
		elif (index == 3):
			self.timerEdit.setText(str(float(self.stepsToStop)/3600000))
		self.freeChanging = False
	
	def changeTimeIndex(self, num):
		self.renameButtonsUnits(num,langRu)
		self.drawStopTime()
			
	def addStopTime(self, time, inc):
		index = self.timeBox.currentIndex()
		indx = index + inc
		if (indx == 0):
			self.stepsToStop = self.stepsToStop + time
		elif (indx == 1):
			self.stepsToStop = self.stepsToStop + 1000*time
		elif (indx == 2):
			self.stepsToStop = self.stepsToStop + 60000*time
		elif (indx == 3):
			self.stepsToStop = self.stepsToStop + 3600000*time
		elif (indx == 4):
			self.stepsToStop = self.stepsToStop + 86400000
		
		if inc:
			if (indx > 3):
				self.drawStopTime()
			else:
				self.timeBox.setCurrentIndex(indx)
		else:
			self.drawStopTime()
		
#program
en = False
for i in sys.argv:
	if i is "e":
		en = True	
			
langRu = not en

app = QApplication(sys.argv)

if langRu:
	translator = QtCore.QTranslator()
	translator.load("qt_ru")
	app.installTranslator(translator)	
	
d = app.desktop()
sw = d.width()
sh = d.height()

if ((sw >= WWIDTH) and (sh >= WHEIGHT)):
	
	
	w = NetworkWindow(sw,sh)
	sys.exit(app.exec_())
	
else:
	print(SMALL_SCREEN[langRu])
