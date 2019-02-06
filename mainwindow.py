# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(875, 378)
        self.imageFrameS = QtWidgets.QFrame(MainWindow)
        self.imageFrameS.setGeometry(QtCore.QRect(20, 20, 320, 240))
        self.imageFrameS.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.imageFrameS.setFrameShadow(QtWidgets.QFrame.Raised)
        self.imageFrameS.setObjectName("imageFrameS")
        self.imageFrameD = QtWidgets.QFrame(MainWindow)
        self.imageFrameD.setGeometry(QtCore.QRect(390, 20, 320, 240))
        self.imageFrameD.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.imageFrameD.setFrameShadow(QtWidgets.QFrame.Raised)
        self.imageFrameD.setObjectName("imageFrameD")
        
        self.captureButton = QtWidgets.QPushButton(MainWindow)
        self.captureButton.setGeometry(QtCore.QRect(740, 20, 101, 31))
        self.captureButton.setCheckable(True)
        self.captureButton.setChecked(True)
        self.captureButton.setObjectName("captureButton")
        self.captureButton.clicked.connect(self.captureButtonAction)
        
        self.colorButton = QtWidgets.QPushButton(MainWindow)
        self.colorButton.setGeometry(QtCore.QRect(740, 60, 101, 31))
        self.colorButton.setCheckable(True)
        self.colorButton.setChecked(False)
        self.colorButton.setObjectName("colorButton")
        self.colorButton.clicked.connect(self.colorButtonAction)
        
        self.loadButton = QtWidgets.QPushButton(MainWindow)
        self.loadButton.setGeometry(QtCore.QRect(740, 100, 101, 31))
        self.loadButton.setObjectName("loadButton")
        
        self.saveButton = QtWidgets.QPushButton(MainWindow)
        self.saveButton.setGeometry(QtCore.QRect(740, 140, 101, 31))
        self.saveButton.setObjectName("saveButton")
        
        self.copyButton = QtWidgets.QPushButton(MainWindow)
        self.copyButton.setGeometry(QtCore.QRect(740, 180, 101, 31))
        self.copyButton.setObjectName("copyButton")
        
        self.resizeButton = QtWidgets.QPushButton(MainWindow)
        self.resizeButton.setGeometry(QtCore.QRect(740, 220, 101, 31))
        self.resizeButton.setObjectName("resizeButton")
        
        self.enlargeButton = QtWidgets.QPushButton(MainWindow)
        self.enlargeButton.setGeometry(QtCore.QRect(740, 260, 101, 31))
        self.enlargeButton.setObjectName("enlargeButton")
        
        self.angleDial = QtWidgets.QDial(MainWindow)
        self.angleDial.setGeometry(QtCore.QRect(40, 260, 81, 91))
        self.angleDial.setObjectName("angleDial")
        self.angleDial.valueChanged.connect(self.dialAction)
        
        self.horizontalSlider = QtWidgets.QSlider(MainWindow)
        self.horizontalSlider.setGeometry(QtCore.QRect(150, 280, 160, 22))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        
        self.verticalSlider = QtWidgets.QSlider(MainWindow)
        self.verticalSlider.setGeometry(QtCore.QRect(340, 280, 160, 22))
        self.verticalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.verticalSlider.setObjectName("verticalSlider")
        
        self.zoomSlider = QtWidgets.QSlider(MainWindow)
        self.zoomSlider.setGeometry(QtCore.QRect(530, 280, 160, 22))
        self.zoomSlider.setOrientation(QtCore.Qt.Horizontal)
        self.zoomSlider.setObjectName("zoomSlider")
        
        self.label = QtWidgets.QLabel(MainWindow)
        self.label.setGeometry(QtCore.QRect(180, 310, 121, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(MainWindow)
        self.label_2.setGeometry(QtCore.QRect(370, 310, 121, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(MainWindow)
        self.label_3.setGeometry(QtCore.QRect(590, 310, 121, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(MainWindow)
        self.label_4.setGeometry(QtCore.QRect(70, 350, 121, 16))
        self.label_4.setObjectName("label_4")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        
    def captureButtonAction(self):
        print("what")
    
    def colorButtonAction(self):
        print("Color")
        
    def loadButtonAction(self):   
        print("Load")
        
    def saveButtonAction(self):    
        print("Save")
    
    def copyButtonAction(self):
        print("Copy")
    
    def resizeButtonAction(self):
        print("Resize")
        
    def enlargeButtonAction(self):
        print("Enlarge")
        
    def dialAction(self):
        print(self.angleDial.value)
        
    def horizontalSliderAction(self):
        print("Horizontal")
    
    def verticalSliderAction(self):
        print("Vertical")
        
    def zoomSliderAction(self):
        print("Zoom")
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Proyecto de Visión Artificial"))
        self.captureButton.setText(_translate("MainWindow", "Stop Capture"))
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

