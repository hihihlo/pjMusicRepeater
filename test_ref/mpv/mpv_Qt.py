import mpv
import time
import os
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Test(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.container = QWidget(self)
        self.setCentralWidget(self.container)
        self.container.setAttribute(Qt.WA_DontCreateNativeAncestors)
        self.container.setAttribute(Qt.WA_NativeWindow)
        player = mpv.MPV(wid=str(int(self.container.winId())),
                #vo='x11',
                log_handler=print,
                loglevel='debug')
        player.play('N0_1.wav')

app = QApplication(sys.argv)

import locale
locale.setlocale(locale.LC_NUMERIC, 'C')
win = Test()
win.show()

sys.exit(app.exec_())