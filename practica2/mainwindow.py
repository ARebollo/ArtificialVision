from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QLabel, QGraphicsScene
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtCore import QRect, QTimer, Qt
import cv2
from cv2 import VideoCapture
import numpy as np
#from ImgViewer import ImgViewer
import copy

class Ui_MainWindow(QtWidgets.QMainWindow):

    
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        print("Trying to connect")
        self.captureButton.clicked.connect(self.captureButtonAction)
        self.pixelTButton.clicked.connect(self.setPixelTransfAction)
        self.kernelButton.clicked.connect(self.setKernelAction)
        self.operOrderButton.clicked.connect(self.setOperationOrderAction)

        '''
        dictionary = {
            1: self.one,
            2: self.two,
            3: self.three,
            4: self.four,
            5: self.five,
            6: self.six,
            7: self.seven,
            8: self.eight,
            9: self.nine,
            10: self.ten,
            11: self.eleven,
            12: self.twelve
        }
        '''
            # Get the function from switcher dictionary
            # TODO
            #func = dictionary.get(valorDesplegable, lambda: "Invalid month")
            # Execute the function
            #print func()

    def captureButtonAction(self):
        pass

    def colorImageAction(self):
        pass

    def loadImageAction(self):
        pass

    def saveImageAction(self):
        pass

    def setPixelTransfAction(self):
        PixelTF = QtWidgets.QDialog()
        uic.loadUi('pixelTForm.ui', PixelTF)
        PixelTF.exec()

    def setKernelAction(self):
        Filter = QtWidgets.QDialog()
        uic.loadUi('lFilterForm.ui', Filter)
        Filter.exec()

    def setOperationOrderAction(self):
        OrderForm = QtWidgets.QDialog()
        uic.loadUi('operOrderForm.ui', OrderForm)
        OrderForm.exec()
    
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())

