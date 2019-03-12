from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QLabel, QGraphicsScene
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtCore import QRect, QTimer, Qt
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

        self.PixelTF = QtWidgets.QDialog()
        uic.loadUi('pixelTForm.ui', self.PixelTF)

        self.Filter = QtWidgets.QDialog()
        uic.loadUi('lFilterForm.ui', self.Filter)

        self.OrderForm = QtWidgets.QDialog()
        uic.loadUi('operOrderForm.ui', self.OrderForm)

        self.capture = VideoCapture(0)
        self.captureState = False

        #Timer to control the capture.
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerLoop)
        self.timer.start(16)
        
        # FIXED: Opencv images where created with wrong width height values (switched) so the copy failed 
        # self.colorImage = np.zeros((320,240))
        # FIXED: original removed 2 of the 3 chanels with the np.zeros
        # self.colorImage = np.zeros((320,240))
        #self.colorImage = np.zeros((240,320,3))
        self.grayImage = np.zeros((240,320))
        self.imgLeft = QImage(320, 240, QImage.Format_RGB888)
        self.imgVisorS = ImgViewer(320,240, self.imgLeft, self.imageFrameS)
        
        self.label_S = QLabel(self.imgVisorS)
        self.label_S.setObjectName("label_S")
        self.label_S.setGeometry(QRect(0, 0, 320, 240))
        self.label_S.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        #TODO: Delete label, set as attribute of imgViewer
        #Isn't it the same? TODO later, it works *for now*        
    
        # FIXED: original removed 2 of the 3 chanels with the np.zeros
        #self.colorImageDest = np.zeros((240,320))
        #self.colorImageDest = np.zeros((240,320,3))
        self.grayImageDest = np.zeros((240,320))
        self.imgRight = QImage(320, 240, QImage.Format_RGB888)
        self.imgVisorD = ImgViewer(320,240, self.imgRight, self.imageFrameD)
        
        self.label_D = QLabel(self.imageFrameD)
        self.label_D.setObjectName("label_D")
        self.label_D.setGeometry(QRect(0, 0, 320, 240))

        # self.visorHistoS = ImgViewer(256, self.ui.histoFrameS.height(), self.ui.histoFrameS)
        # self.visorHistoD = ImgViewer(256, self.ui.histoFrameS.height(), self.ui.histoFrameD)
        
        self.captureButton.clicked.connect(self.captureButtonAction)
        self.loadButton.clicked.connect(self.loadImageAction)
        self.pixelTButton.clicked.connect(self.setPixelTransfAction)
        self.kernelButton.clicked.connect(self.setKernelAction)
        self.operOrderButton.clicked.connect(self.setOperationOrderAction)

        #self.retranslateUi(MainWindow)
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

        
        dictionary = {
            'Transform Pixel': self.transformPixelAction,
            'Thresholding': self.thresholdingAction,
            'Equalize': self.equalizeAction,
            4: self.Gaussian Blur,
            5: self.Median Blur,
            6: self.Linear Filter,
            7: self.Dilate,
            8: self.Erode,
            9: self.Apply Several...,
        }
        
            # Get the function from switcher dictionary
            # TODO
            #func = dictionary.get(valorDesplegable, lambda: "Invalid month")
            # Execute the function
            #print func()

    def transformPixelAction(self):
        pass

    def thresholdingAction(self):
        pass

    def equalizeAction(self):
        pass

    def gaussianBlurAction(self):
        pass

    def medianBlurAction(self):
        pass

    def linearFilterAction(self):
        pass

    def dilateAction(self):
        pass

    def erodeAction(self):
        pass

    def applySeveralAction(self):
        pass

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
            ret, self.grayImage = self.capture.read()
            self.grayImage = cv2.resize(self.grayImage, (320,240))
            self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)    
            # FIXED: astype is needed to convert the cv type to the qt expected one
            self.imgVisorS.qimg = QImage(self.grayImage.astype(np.int8), self.grayImage.shape[1], self.grayImage.shape[0],self.grayImage.strides[0], QImage.Format_Grayscale8)
            # FIXED: astype is needed to convert the cv type to the qt expected one
            self.imgVisorD.qimg = QImage(self.grayImageDest.astype(np.int8), self.grayImageDest.shape[1], self.grayImageDest.shape[0], QImage.Format_Grayscale8)
            print(self.operationComboBox.currentText())
            self.label_S.setPixmap(QPixmap.fromImage(self.imgVisorS.qimg))
            self.label_D.setPixmap(QPixmap.fromImage(self.imgVisorD.qimg))
            self.imgVisorS.repaint()
            self.imgVisorS.update()

    def colorImageAction(self):
        pass

    def loadImageAction(self):
        print("Load")
        self.imgPath, _ = QFileDialog.getOpenFileName()
        if self.captureState == True:
            self.captureButtonAction()
                
        self.grayImage = cv2.imread(self.imgPath)
        self.grayImage = cv2.resize(self.grayImage, (320,240))
        self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)
        
        # TODO: remove to avoid double setting here and in the loopTimer method
        self.imgLeft = QImage(self.grayImage, self.grayImage.shape[1], self.grayImage.shape[0], QImage.Format_Grayscale8)
        
        self.label_S.setPixmap(QPixmap.fromImage(self.imgLeft))
        
        print(self.imgPath)

    def saveImageAction(self):
        saveImage = self.grayImage    
        filename = QFileDialog.getSaveFileName()
        cv2.imWrite(filename, saveImage)
        print("Save")

    def setPixelTransfAction(self):
        self.PixelTF.exec()

    def setKernelAction(self):
        self.Filter.exec()

    def setOperationOrderAction(self):
        self.OrderForm.exec()
    
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())

