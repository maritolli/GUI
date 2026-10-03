from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

import cl1
import cl2

class Some(QMainWindow):
    def __init__(self):
        super().__init__()
        self.myClsig = cl1.mySignal

class Data:
    def __init__(self):
        self.myData = []

    def getData(self):
        return self.myData

if __name__ == "__main__":
    cl1.func()
    app = QApplication(sys.argv)
    window = Some()
    window.show()
    app.exec()