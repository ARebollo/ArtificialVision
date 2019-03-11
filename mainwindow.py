# -*- coding: utf-8 -*-

import copy

import cv2
import numpy as np
# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QRect, QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog, QLabel, QMainWindow, QFrame
from cv2 import VideoCapture

from ImgViewer import ImgViewer


class MainWindow(QMainWindow):

    #path to the image, and storage of the origin and transformed image
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = uic.loadUi("mainwindow.ui", self)
        # self.ui.setupUI(self)
        self.imgPath = ""
        self.capture = VideoCapture(0)
        self.captureState = False
        self.colorState = False  #False =  color, true = gray
        self.winSelected = False
        self.warpState = False

        #Timer to control the capture.
        self.timer = QTimer()
        self.timer.timeout.connect(self.compute)
        self.timer.start(16)


        #Values for window selection
        self.rectHeight = 0
        self.rectWidth = 0
        self.posX = 0
        self.posY = 0

        #Signals for window selection


        #Left image frame. Image prior to transformation
        # self.imageFrameS = QFrame(MainWindow)
        # self.imageFrameS.setGeometry(QtCore.QRect(20, 20, 320, 240))
        # self.imageFrameS.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # self.imageFrameS.setFrameShadow(QtWidgets.QFrame.Raised)
        # # self.imageFrameS.setObjectName("imageFrameS")
        # FIXED: Opencv images where created with wrong width height values (switched) so the copy failed
        self.colorImage = np.zeros((320,240))
        # FIXED: original removed 2 of the 3 channels with the np.zeros
        self.colorImage = np.zeros((320,240))
        self.colorImage = np.zeros((240,320,3))
        self.grayImage = np.zeros((240,320))
        self.imgLeft = QImage(320, 240, QImage.Format_RGB888)
        self.imgVisorS = ImgViewer(320,240, self.imgLeft, self.imageFrameS)
        self.imgVisorS.windowSelected.connect(self.selectWindow)
        self.label_S = QLabel(self.imgVisorS)
        self.label_S.setObjectName("label_S")
        self.label_S.setGeometry(QRect(0, 0, 320, 240))
        self.label_S.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        # #TODO: Delete label, set as attribute of imgViewer
        # #Isn't it the same? TODO later, it works *for now*
        #
        # #Right image frame. Image after transformation.
        # self.imageFrameD = QtWidgets.QFrame(MainWindow)
        # self.imageFrameD.setGeometry(QtCore.QRect(390, 20, 320, 240))
        # self.imageFrameD.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # self.imageFrameD.setFrameShadow(QtWidgets.QFrame.Raised)
        # self.imageFrameD.setObjectName("imageFrameD")
        # FIXED: original removed 2 of the 3 chanels with the np.zeros
        self.colorImageDest = np.zeros((240,320))
        self.colorImageDest = np.zeros((240,320,3))
        self.grayImageDest = np.zeros((240,320))
        self.imgRight = QImage(320, 240, QImage.Format_RGB888)
        self.imgVisorD = ImgViewer(320,240, self.imgRight, self.imageFrameD)
        #
        self.label_D = QLabel(self.imageFrameD)
        self.label_D.setObjectName("label_D")
        self.label_D.setGeometry(QRect(0, 0, 320, 240))
        #
        # #Capture button.
        self.captureButton.clicked.connect(self.captureButtonAction)
        #
        # #Gray/Color button.
        self.colorButton.clicked.connect(self.colorButtonAction)
        #
        # #Load from file button.
        self.loadButton.clicked.connect(self.loadButtonAction)
        #
        # #Save to file button.
        self.saveButton.clicked.connect(self.saveButtonAction)


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

    def compute(self):
        if (self.captureState == True and self.capture.isOpened() == True):

            if self.colorState == False:
                ret, self.colorImage = self.capture.read()
                #print("Captured shape %s"%str(self.colorImage.shape))
                self.colorImage = cv2.resize(self.colorImage, (320, 240))
                #print("Resized shape %s"%str(self.colorImage.shape))
                self.colorImage = cv2.cvtColor(self.colorImage, cv2.COLOR_BGR2RGB)
                # FIXED: astype is needed to convert the cv type to the qt expected one
                self.imgVisorS.qimg = QImage(self.colorImage.astype(np.int8), self.colorImage.shape[1], self.colorImage.shape[0], QImage.Format_RGB888)
                #self.colorImageDest = self.colorImage
                # FIXED: astype is needed to convert the cv type to the qt expected one
                self.imgVisorD.qimg = QImage(self.colorImageDest.astype(np.int8), self.colorImageDest.shape[1], self.colorImageDest.shape[0], QtGui.QImage.Format_RGB888)

            else:
                ret, self.grayImage = self.capture.read()
                self.grayImage = cv2.resize(self.grayImage, (320,240))
                self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)
                # TODO: I don't think Source image have to be put in grayscale
                # FIXED: astype is needed to convert the cv type to the qt expected one
                self.imgVisorS.qimg = QImage(self.grayImage.astype(np.int8), self.grayImage.shape[1], self.grayImage.shape[0],self.grayImage.strides[0], QImage.Format_Grayscale8)
                # FIXED: astype is needed to convert the cv type to the qt expected one
                self.imgVisorD.qimg = QImage(self.grayImageDest.astype(np.int8), self.grayImageDest.shape[1], self.grayImageDest.shape[0], QImage.Format_Grayscale8)

            #To update the warping in real time. TODO translation
            if self.warpState == True:
                rotation_matrix = cv2.getRotationMatrix2D((320/2,240/2), -self.angleDial.value(),1+self.zoomSlider.value()/3)
                translation_matrix = np.float32([[1,0,self.horizontalSlider.value()],[0,1,self.verticalSlider.value()]])
                if self.colorState == False:
                    rotated_image = cv2.warpAffine(self.colorImage, rotation_matrix, (320,240))
                    rotated_image = cv2.warpAffine(rotated_image, translation_matrix, (320,240))
                    self.colorImageDest = rotated_image
                    self.imgVisorD.qimg = QImage(self.colorImageDest.astype(np.int8), self.colorImageDest.shape[1], self.colorImageDest.shape[0], QtGui.QImage.Format_RGB888)
                else:
                    rotated_image = cv2.warpAffine(self.grayImage, rotation_matrix, (320,240))
                    rotated_image = cv2.warpAffine(rotated_image, translation_matrix, (320,240))
                    self.grayImageDest = rotated_image
                    self.imgVisorD.qimg = QImage(self.grayImageDest.astype(np.int8), self.grayImageDest.shape[1], self.grayImageDest.shape[0], QImage.Format_Grayscale8)
            if self.winSelected == True:
                self.imgVisorS.drawSquare(self.posX, self.posY, self.rectWidth,self.rectHeight)
            self.label_S.setPixmap(QPixmap.fromImage(self.imgVisorS.qimg))
            self.label_D.setPixmap(QPixmap.fromImage(self.imgVisorD.qimg))
            self.imgVisorS.repaint()
            self.imgVisorS.update()

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
        if self.captureState == True:
            self.captureButtonAction()


        self.colorImage = cv2.imread(self.imgPath)
        self.colorImage = cv2.resize(self.colorImage, (320,240))
        self.colorImage = cv2.cvtColor(self.colorImage, cv2.COLOR_BGR2RGB)


        self.grayImage = cv2.imread(self.imgPath)
        self.grayImage = cv2.resize(self.grayImage, (320,240))
        self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)

        # TODO: remove to avoid double setting here and in the loopTimer method
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



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
