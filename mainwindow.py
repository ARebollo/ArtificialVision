# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QRect, QTimer
import cv2
from cv2 import VideoCapture
import numpy as np
#import ImgViewer

    

class Ui_MainWindow(object):
    

    #path to the image, and storage of the origin and transformed image

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(875, 378)
        
        self.imgPath = ""
        self.capture = VideoCapture(0)
        self.captureState = False
        self.colorState = False  #False =  color, true = gray

        #Timer to control the capture.
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerLoop)
        self.timer.start(16)
        
        #Left image frame. Image prior to transformation
        self.imageFrameS = QtWidgets.QFrame(MainWindow)
        self.imageFrameS.setGeometry(QtCore.QRect(20, 20, 320, 240))
        self.imageFrameS.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.imageFrameS.setFrameShadow(QtWidgets.QFrame.Raised)
        self.imageFrameS.setObjectName("imageFrameS")
        self.colorImage = np.zeros(1)
        self.grayImage = np.zeros(1)
        self.imgLeft = QImage()
        #self.imgVisorS = ImgViewer(320,240, self.imgLeft, self.imageFrameS)
        
        
        self.label_S = QLabel(self.imageFrameS)
        self.label_S.setObjectName("label_S")
        self.label_S.setGeometry(QRect(0, 0, 320, 240))
        
        #Right image frame. Image after transformation.
        self.imageFrameD = QtWidgets.QFrame(MainWindow)
        self.imageFrameD.setGeometry(QtCore.QRect(390, 20, 320, 240))
        self.imageFrameD.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.imageFrameD.setFrameShadow(QtWidgets.QFrame.Raised)
        self.imageFrameD.setObjectName("imageFrameD")
        self.colorImageDest = np.zeros(1)
        self.grayImageDest = np.zeros(1)
        self.imgRight = QImage()
        #self.imgVisorD = ImgViewer(320,240, self.imgRight, self.imageFrameD)
        
        self.label_D = QLabel(self.imageFrameD)
        self.label_D.setObjectName("label_D")
        self.label_D.setGeometry(QRect(0, 0, 320, 240))
        
        #Capture button.
        self.captureButton = QtWidgets.QPushButton(MainWindow)
        self.captureButton.setGeometry(QtCore.QRect(740, 20, 101, 31))
        self.captureButton.setCheckable(True)
        self.captureButton.setChecked(False)
        self.captureButton.setObjectName("captureButton")
        self.captureButton.clicked.connect(self.captureButtonAction)
        
        #Gray/Color button.
        self.colorButton = QtWidgets.QPushButton(MainWindow)
        self.colorButton.setGeometry(QtCore.QRect(740, 60, 101, 31))
        self.colorButton.setCheckable(True)
        self.colorButton.setChecked(False)
        self.colorButton.setObjectName("colorButton")
        self.colorButton.clicked.connect(self.colorButtonAction)
        
        #Load from file button.
        self.loadButton = QtWidgets.QPushButton(MainWindow)
        self.loadButton.setGeometry(QtCore.QRect(740, 100, 101, 31))
        self.loadButton.setObjectName("loadButton")
        self.loadButton.clicked.connect(self.loadButtonAction)
        
        #Save to file button.
        self.saveButton = QtWidgets.QPushButton(MainWindow)
        self.saveButton.setGeometry(QtCore.QRect(740, 140, 101, 31))
        self.saveButton.setObjectName("saveButton")
        self.saveButton.clicked.connect(self.saveButtonAction)
        
        #Copy selection button.
        self.copyButton = QtWidgets.QPushButton(MainWindow)
        self.copyButton.setGeometry(QtCore.QRect(740, 180, 101, 31))
        self.copyButton.setObjectName("copyButton")
        self.copyButton.clicked.connect(self.copyButtonAction)
        
        #Resize image button.
        self.resizeButton = QtWidgets.QPushButton(MainWindow)
        self.resizeButton.setGeometry(QtCore.QRect(740, 220, 101, 31))
        self.resizeButton.setObjectName("resizeButton")
        self.resizeButton.clicked.connect(self.resizeButtonAction)
        
        #Enlarge image button
        self.enlargeButton = QtWidgets.QPushButton(MainWindow)
        self.enlargeButton.setGeometry(QtCore.QRect(740, 260, 101, 31))
        self.enlargeButton.setObjectName("enlargeButton")
        self.enlargeButton.clicked.connect(self.enlargeButtonAction)
        
        #Angle dial
        self.angleDial = QtWidgets.QDial(MainWindow)
        self.angleDial.setGeometry(QtCore.QRect(40, 260, 81, 91))
        self.angleDial.setObjectName("angleDial")
        self.angleDial.setMinimum(0)
        self.angleDial.setMaximum(359)
        self.angleDial.setValue(0)
        self.angleDial.setWrapping(True)
        self.angleDial.valueChanged.connect(self.dialAction)
        
        #Horizontal translation slider
        self.horizontalSlider = QtWidgets.QSlider(MainWindow)
        self.horizontalSlider.setGeometry(QtCore.QRect(150, 280, 160, 22))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalSlider.setMinimum(-100)
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setValue(0)
        self.horizontalSlider.valueChanged.connect(self.horizontalSliderAction)
        
        #Vertical translation slider
        self.verticalSlider = QtWidgets.QSlider(MainWindow)
        self.verticalSlider.setGeometry(QtCore.QRect(340, 280, 160, 22))
        self.verticalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.verticalSlider.setObjectName("verticalSlider")
        self.verticalSlider.setMinimum(-80)
        self.verticalSlider.setMaximum(80)
        self.verticalSlider.setValue(0)
        self.verticalSlider.valueChanged.connect(self.verticalSliderAction)
        
        #Zoom slider
        self.zoomSlider = QtWidgets.QSlider(MainWindow)
        self.zoomSlider.setGeometry(QtCore.QRect(530, 280, 160, 22))
        self.zoomSlider.setOrientation(QtCore.Qt.Horizontal)
        self.zoomSlider.setObjectName("zoomSlider")
        self.zoomSlider.setMinimum(-50)
        self.zoomSlider.setMaximum(50)
        self.zoomSlider.setValue(0)
        self.zoomSlider.valueChanged.connect(self.zoomSliderAction)
        
        #Labels, in the order [Angle, Horizontal, Vertical, Zoom]
        self.label = QtWidgets.QLabel(MainWindow)
        self.label.setGeometry(QtCore.QRect(180, 310, 121, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(MainWindow)
        self.label_2.setGeometry(QtCore.QRect(380, 310, 121, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(MainWindow)
        self.label_3.setGeometry(QtCore.QRect(600, 310, 121, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(MainWindow)
        self.label_4.setGeometry(QtCore.QRect(70, 350, 121, 16))
        self.label_4.setObjectName("label_4")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        
    def captureButtonAction(self):
        if self.captureState == False:
            self.captureButton.setText("Stop Capture")
            self.captureButton.setChecked(True)
            print("Started")
            self.captureState = True
        else: 
            self.captureButton.setText("Start Capture")
            self.captureButton.setChecked(False)
            print("Stopped")
            self.captureState = False

    def timerLoop(self):
        if (self.captureState == True and self.capture.isOpened() == True):
            if self.colorState == False:
                ret, colorImage = self.capture.read()
                self.colorImage = cv2.resize(self.colorImage, (320,240))
                #self.colorImage = cv2.cvtColor(self.colorImage, cv2.COLOR_BGR2RGB)
                self.imgLeft = QImage(self.colorImage, self.colorImage.shape[1], self.colorImage.shape[0],                                                                                                                                                 
                         QImage.Format_RGB888)    
                
            else:
                ret, grayImage = self.capture.read()
                self.grayImage = cv2.resize(self.grayImage, (320,240))
                #self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)    
                self.imgLeft = QImage(self.grayImage, self.grayImage.shape[1], self.grayImage.shape[0],                                                                                                                                                 
                         QImage.Format_Grayscale8)
                
                
            self.label_S.setPixmap(QPixmap.fromImage(self.imgLeft))
            
    def colorButtonAction(self):
        if self.colorState == False:
            self.colorButton.setText("Gray Image")
            self.colorButton.setChecked(True)
            print("Swapping to Gray")
            self.colorState = True
        else: 
            self.colorButton.setText("Color Image")
            self.colorButton.setChecked(False)
            print("Swapping to color")
            self.colorState = False
        
    def loadButtonAction(self):   
        print("Load")
        self.imgPath, _ = QFileDialog.getOpenFileName()
        
        
        self.colorImage = cv2.imread(self.imgPath)
        self.colorImage = cv2.resize(self.colorImage, (320,240))
        self.colorImage = cv2.cvtColor(self.colorImage, cv2.COLOR_BGR2RGB)
        
        
        self.grayImage = cv2.imread(self.imgPath)
        self.grayImage = cv2.resize(self.grayImage, (320,240))
        self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)
        
        if self.colorState == False:
            self.imgLeft = QImage(self.colorImage, self.colorImage.shape[1], self.colorImage.shape[0],                                                                                                                                                 
                         QImage.Format_RGB888)
        else:
            self.imgLeft = QImage(self.grayImage, self.grayImage.shape[1], self.grayImage.shape[0],                                                                                                                                                 
                         QImage.Format_Grayscale8)
        

        self.label_S.setPixmap(QPixmap.fromImage(self.imgLeft))
        
        print(self.imgPath)
        
    def saveButtonAction(self):
        if self.colorState ==  False:
            saveImage = self.colorImage
            saveImage = cv2.cvtColor(saveImage, cv2.COLOR_RGB2BGR)
        else:
            saveImage = self.grayImage    

        filename = QFileDialog.getSaveFileName()
        cv2.imWrite(filename, saveImage)
        print("Save")
    
    def copyButtonAction(self):
        print("Copy")
    
    def resizeButtonAction(self):
        print("Resize")
        
    def enlargeButtonAction(self):
        print("Enlarge")
        
    def dialAction(self):
        print(self.angleDial.value())
        
    def horizontalSliderAction(self):
        print(self.horizontalSlider.value())
    
    def verticalSliderAction(self):
        print(self.verticalSlider.value())
        
    def zoomSliderAction(self):
        print("Zoom")
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Proyecto de Visión Artificial"))
        self.captureButton.setText(_translate("MainWindow", "Start Capture"))
        self.colorButton.setText(_translate("MainWindow", "Color Image"))
        self.loadButton.setText(_translate("MainWindow", "Load from File"))
        self.saveButton.setText(_translate("MainWindow", "Save to File"))
        self.copyButton.setText(_translate("MainWindow", "Copy"))
        self.resizeButton.setText(_translate("MainWindow", "Resize"))
        self.enlargeButton.setText(_translate("MainWindow", "Enlarge"))
        self.label.setText(_translate("MainWindow", "Horizontal Translation"))
        self.label_2.setText(_translate("MainWindow", "Vertical Translation"))
        self.label_3.setText(_translate("MainWindow", "Zoom"))
        self.label_4.setText(_translate("MainWindow", "Angle"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_MainWindow()
    ui.setupUi(Dialog)
    Dialog.show()

    sys.exit(app.exec_())