from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QLabel, QGraphicsScene
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtCore import QRect, QTimer, Qt, QLineF
import cv2
from cv2 import VideoCapture
import numpy as np
#from ImgViewer import ImgViewer
import copy
from ImgViewer import ImgViewer

class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        print("Trying to connect")

        self.addObject =  QtWidgets.QDialog()
        uic.loadUi('objectName.ui', self.addObject)
        self.addObject.okButton.clicked.connect(self.addOkAction)

        self.capture = VideoCapture(0)
        self.captureState = True
        self.captureButtonAction()

        #Timer to control the capture.
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerLoop)
        self.timer.start(16)
        
        # FIXED: Opencv images where created with wrong width height values (switched) so the copy failed 
        # self.colorImage = np.zeros((320,240))
        # FIXED: original removed 2 of the 3 chanels with the np.zeros
        # self.colorImage = np.zeros((320,240))
        #self.colorImage = np.zeros((240,320,3))
        self.grayImage = np.zeros((240, 320), np.uint8)
        # self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)
        self.imgS = QImage(320, 240, QImage.Format_Grayscale8)
        self.visorS = ImgViewer(320, 240, self.imgS, self.imageFrameS)
        
        #self.visorS.set_open_cv_image(self.grayImage)
        
        # FIXED: original removed 2 of the 3 chanels with the np.zeros
        #self.colorImageDest = np.zeros((240,320))
        #self.colorImageDest = np.zeros((240,320,3))
        self.grayImageDest = np.zeros((240,320), np.uint8)
        # self.grayImage = cv2.cvtColor(self.grayImageDest, cv2.COLOR_BGR2GRAY)
        self.imgD = QImage(320, 240, QImage.Format_Grayscale8)
        self.visorD = ImgViewer(320, 240, self.imgD, self.imageFrameD)
        
        #self.visorS.set_open_cv_image(self.grayImageDest)

        self.captureButton.clicked.connect(self.captureButtonAction)

        self.addButton.clicked.connect(self.addAction)
        self.removeButton.clicked.connect(self.removeAction)
        
        #self.retranslateUi(MainWindow)
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def addAction(self):
        self.addObject.show()
        print("Add")

    def addOkAction(self):
        #Add object to list
        self.addObject.hide()
        pass
    def removeAction(self):
        pass

    def captureButtonAction(self):
        if self.captureState is False:
            self.captureButton.setChecked(True)
            self.captureButton.setText("Stop Capture")
            self.captureState = True
        else:
            self.captureState = False
            self.captureButton.setChecked(False)
            self.captureButton.setText("Start Capture")

    def selectWindow(self, point, posX, posY):
        pEnd = QtCore.QPointF()
        if posX > 0 and posY > 0:
            self.posX = int(point.x() - posX/2)
        if self.posX < 0:
            self.posX = 0
        self.posY = int(point.y()-posY/2)
        if self.posY < 0:
            self.posY = 0
        pEnd.setX(point.x()+posX/2)
        if pEnd.x() >= 320:
            pEnd.setX(319)
        pEnd.setY(point.y()+posY/2)
        if pEnd.y() >= 240:
            pEnd.setY(239)
        self.rectWidth = int(pEnd.x() - self.posX+1)
        self.rectHeight = int(pEnd.y() - self.posY+1)
        print("Values: " + str(self.posX)+ " " + str(self.posY) + " " + str(self.rectWidth) +" "+ str(self.rectHeight))
        self.winSelected = True

    def timerLoop(self):
        if (self.captureState == True and self.capture.isOpened() == True):
            ret, self.grayImage = self.capture.read()
            self.grayImage = cv2.resize(self.grayImage, (320, 240))
            self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)


            



            # self.label_S.setPixmap(QPixmap.fromImage(self.visorS.qimg))
            # self.label_D.setPixmap(QPixmap.fromImage(self.imgVisorD.qimg))
            # self.visorS.repaint()
            # self.visorS.update()
        
        # FIXED: astype is needed to convert the cv type to the qt expected one
        self.visorS.set_open_cv_image(self.grayImage)
        # FIXED: astype is needed to convert the cv type to the qt expected one
        self.visorD.set_open_cv_image(self.grayImageDest)
        self.visorS.update()
        self.visorD.update()

    
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())