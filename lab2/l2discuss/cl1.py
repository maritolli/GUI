from PyQt5.QtCore import pyqtSignal
import main

mySignal = pyqtSignalRub(int)

def func():
    newOne = main.Data()
    newList = newOne.getData()

func()