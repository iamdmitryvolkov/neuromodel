# gui 2.0 starter
# 30.09.2015 Dmitry Volkov

# QT5
import sys
from PyQt5.QtWidgets import QApplication

# GUI
from gui_window import *
from gui_consts import *

# program
app = QApplication(sys.argv)

d = app.desktop()
sw = d.width()
sh = d.height()

if (sw >= WWIDTH) and (sh >= WHEIGHT):
    w = NetworkWindow()
    sys.exit(app.exec_())
else:
    print(SMALL_SCREEN_TEXT)
