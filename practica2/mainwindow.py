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

        self.PixelTF = QtWidgets.QDialog()
        uic.loadUi('pixelTForm.ui', self.PixelTF)
        self.PixelTF.okButton.clicked.connect(self.closePixelTransformAction)

        self.Filter = QtWidgets.QDialog()
        uic.loadUi('lFilterForm.ui', self.Filter)
        self.Filter.okButton.clicked.connect(self.closeFilterFormAction)

        self.OrderForm = QtWidgets.QDialog()
        uic.loadUi('operOrderForm.ui', self.OrderForm)
        self.OrderForm.okButton.clicked.connect(self.closeOrderFormAction)

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
        

        #TODO: Delete label, set as attribute of imgViewer
        #Isn't it the same? TODO later, it works *for now*        
    
        # FIXED: original removed 2 of the 3 chanels with the np.zeros
        #self.colorImageDest = np.zeros((240,320))
        #self.colorImageDest = np.zeros((240,320,3))
        self.grayImageDest = np.zeros((240,320), np.uint8)
        # self.grayImage = cv2.cvtColor(self.grayImageDest, cv2.COLOR_BGR2GRAY)
        self.imgD = QImage(320, 240, QImage.Format_Grayscale8)
        self.visorD = ImgViewer(320, 240, self.imgD, self.imageFrameD)
        
        #self.visorS.set_open_cv_image(self.grayImageDest)


        self.visorHistoS = ImgViewer(256, self.histoFrameS.height(), None, self.histoFrameS)
        self.visorHistoD = ImgViewer(256, self.histoFrameD.height(), None, self.histoFrameD)


        self.captureButton.clicked.connect(self.captureButtonAction)
        self.loadButton.clicked.connect(self.loadImageAction)
        self.pixelTButton.clicked.connect(self.setPixelTransfAction)
        self.kernelButton.clicked.connect(self.setKernelAction)
        self.operOrderButton.clicked.connect(self.setOperationOrderAction)

        #self.retranslateUi(MainWindow)
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

        
        self.dictionary = {
            'Transform pixel': self.transformPixelAction,
            'Thresholding': self.thresholdingAction,
            'Equalize': self.equalizeAction,
            'Gaussian Blur': self.gaussianBlurAction,
            'Median Blur': self.medianBlurAction,
            'Linear Filter': self.linearFilterAction,
            'Dilate': self.dilateAction,
            'Erode': self.erodeAction,
            'Apply several...': self.applySeveralAction,
        }
        
        self.operationDictionary = {
            'User Defined ': 'test',
            'Negative': 'test2',
            'Brighten': 'test3',
            'Darken': 'test4'
        }
        
            # Get the function from switcher dictionary
            # TODO
            #func = dictionary.get(valorDesplegable, lambda: "Invalid month")
            # Execute the function
            #print func()

    def transformPixelAction(self, startImage):

        lutTable = np.ones((256), np.uint8)

        src_1 = self.PixelTF.origPixelBox1.value()
        src_2 = self.PixelTF.origPixelBox2.value()
        src_3 = self.PixelTF.origPixelBox3.value()
        src_4 = self.PixelTF.origPixelBox4.value()

        dst_1 = self.PixelTF.newPixelBox1.value()
        dst_2 = self.PixelTF.newPixelBox2.value()
        dst_3 = self.PixelTF.newPixelBox3.value()
        dst_4 = self.PixelTF.newPixelBox4.value()

        self.applyTransformPixel(src_1, src_2, dst_1, dst_2, lutTable)
        self.applyTransformPixel(src_2, src_3, dst_2, dst_3, lutTable)
        self.applyTransformPixel(src_3, src_4 + 1, dst_3, dst_4 + 1, lutTable)

        returnImage = cv2.LUT(startImage, lutTable)
        return returnImage

    def applyTransformPixel(self, src1, src2, dst1, dst2, lut):
        for src in range(src1,src2):
            s = ((dst2 - dst1))/(src2 - src1)*(src - src1) + dst1
            lut[src] = s
        
    def thresholdingAction(self, startImage):
        _, returnImage = cv2.threshold(startImage, self.thresholdSpinBox.value(), 255, cv2.THRESH_BINARY)
        return returnImage

    def equalizeAction(self, startImage):
        returnImage = cv2.equalizeHist(startImage)
        return returnImage

    def gaussianBlurAction(self, startImage):
        size = (int(self.gaussWidthBox.cleanText()), int(self.gaussWidthBox.cleanText()))
        returnImage = cv2.GaussianBlur(startImage,ksize = size, sigmaX = 0, sigmaY = 0)
        return returnImage

    def medianBlurAction(self, startImage):
        returnImage = cv2.medianBlur(startImage, ksize = 3)
        return returnImage

    def linearFilterAction(self, startImage):
        kernel = np.zeros((3,3), dtype = np.double)
        for i in range (1,4):
            for j in range (1,4):
                result = 'kernelBox' + str(i) + str(j)
                kernel[i-1,j-1] = getattr(self.Filter, result).value()
        
        returnImage = cv2.filter2D(startImage, ddepth = cv2.CV_8U, kernel = kernel, delta = self.Filter.addedVBox.value())
        return returnImage

    def dilateAction(self, startImage):
        kernel = np.ones((3,3), np.uint8)
        _, returnImage = cv2.threshold(startImage, self.thresholdSpinBox.value(), 255, cv2.THRESH_BINARY)
        returnImage = cv2.dilate(returnImage, kernel, iterations=1)
        return returnImage

    def erodeAction(self, startImage):
        kernel = np.ones((3,3), np.uint8)
        _, returnImage = cv2.threshold(startImage, self.thresholdSpinBox.value(), 255, cv2.THRESH_BINARY)
        returnImage = cv2.erode(returnImage, kernel, iterations=1)
        return returnImage

    def applySeveralAction(self, startImage):

        returnImage = startImage

        if self.OrderForm.firstOperCheckBox.isChecked() is True:
            func = self.dictionary.get(self.OrderForm.operationComboBox1.currentText())
            returnImage = func(returnImage)
        

        if self.OrderForm.secondOperCheckBox.isChecked() is True:
            func = self.dictionary.get(self.OrderForm.operationComboBox2.currentText())
            returnImage = func(returnImage)

        if self.OrderForm.thirdOperCheckBox.isChecked() is True:
            func = self.dictionary.get(self.OrderForm.operationComboBox3.currentText())
            returnImage = func(returnImage)

        if self.OrderForm.fourthOperCheckBox.isChecked() is True:
            func = self.dictionary.get(self.OrderForm.operationComboBox4.currentText())
            returnImage = func(returnImage)
        return returnImage

    def closeOrderFormAction(self):
        self.OrderForm.hide()

    def closePixelTransformAction(self):
        self.PixelTF.hide()

    def closeFilterFormAction(self):
        self.Filter.hide()
        
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
            self.grayImage = cv2.resize(self.grayImage, (320, 240))
            self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)

            print(self.operationComboBox.currentText())

            



            # self.label_S.setPixmap(QPixmap.fromImage(self.visorS.qimg))
            # self.label_D.setPixmap(QPixmap.fromImage(self.imgVisorD.qimg))
            # self.visorS.repaint()
            # self.visorS.update()
        func = self.dictionary.get(self.operationComboBox.currentText())
        self.grayImageDest = func(self.grayImage)
        self.updateHistograms(self.grayImage, self.visorHistoS)
        self.updateHistograms(self.grayImageDest, self.visorHistoD)
        # FIXED: astype is needed to convert the cv type to the qt expected one
        self.visorS.set_open_cv_image(self.grayImage)
        # FIXED: astype is needed to convert the cv type to the qt expected one
        self.visorD.set_open_cv_image(self.grayImageDest)
        self.visorS.update()
        self.visorD.update()

    def colorImageAction(self):
        pass

    def loadImageAction(self):
        print("Load")
        self.imgPath, _ = QFileDialog.getOpenFileName()
        if self.captureState == True:
            self.captureButtonAction()
                
        self.grayImage = cv2.imread(self.imgPath)
        self.grayImage = cv2.resize(self.grayImage, (320, 240))
        self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)
        
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

    def updateHistograms(self, image, visor):
        histoSize = 256
        range = [0, 256]


        # cv2.calcHist(image, 1, channels, nONE, histogram, 1, histoSize, ranges, True, False )
        histogram = cv2.calcHist(images=[image.astype(np.uint8)], channels=[0], mask=None, histSize=[histoSize], ranges=range, hist=True, accumulate=False)
        minH, maxH,_,_ = cv2.minMaxLoc(histogram)

        maxY = visor.height()

        for i, hVal in enumerate(histogram):
            minY = maxY - hVal * maxY / maxH
            visor.drawLine(QLineF(i, minY, i, maxY), Qt.red)
        visor.update()
    
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())