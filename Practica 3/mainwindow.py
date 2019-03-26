from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QLabel, QGraphicsScene
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtCore import QRect, QTimer, Qt, QLineF, QPointF
import cv2
from cv2 import VideoCapture
import numpy as np
#from ImgViewer import ImgViewer
import copy
from ImgViewer import ImgViewer

class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        uic.loadUi('/home/salabeta/ArtificialVision/Practica 3/mainwindow.ui', self)
        print("Trying to connect")

        self.addObject =  QtWidgets.QDialog()
        uic.loadUi('/home/salabeta/ArtificialVision/Practica 3/objectName.ui', self.addObject)
        self.addObject.okButton.clicked.connect(self.addOkAction)

        self.renameObject =  QtWidgets.QDialog()
        uic.loadUi('/home/salabeta/ArtificialVision/Practica 3/objectRename.ui', self.renameObject)
        self.renameObject.okButton.clicked.connect(self.renameOkAction)

        self.capture = VideoCapture(0)
        self.captureState = True
        self.captureButtonAction()

        self.imageWindow = QRect()

        self.winSelected = False
        self.actionReady = False
 
        #Timer to control the capture.
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerLoop)
        self.timer.start(16)
        
        # FIXED: Opencv images where created with wrong width height values (switched) so the copy failed 
        # FIXED: original removed 2 of the 3 chanels with the np.zeros
        self.grayImage = np.zeros((240, 320), np.uint8)
        # self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)
        self.imgS = QImage(320, 240, QImage.Format_Grayscale8)
        self.visorS = ImgViewer(320, 240, self.imgS, self.imageFrameS)

        # FIXED: original removed 2 of the 3 chanels with the np.zeros

        self.grayImageDest = np.zeros((240,320), np.uint8)
        self.imgD = QImage(320, 240, QImage.Format_Grayscale8)
        self.visorD = ImgViewer(320, 240, self.imgD, self.imageFrameD)

        self.colorImageM = np.zeros((240, 700, 3))
        self.imgM = QImage(700, 240, QImage.Format_RGB888)
        self.visorM = ImgViewer(700, 240, self.imgM, self.imageFrameS_2)
        
        #self.visorS.set_open_cv_image(self.grayImageDest)

        self.captureButton.clicked.connect(self.captureButtonAction)

        self.addButton.clicked.connect(self.addAction)
        self.renameButton.clicked.connect(self.renameAction)
        self.removeButton.clicked.connect(self.removeAction)

        self.imageList = []
        self.mapObjects = {}

        self.load1.clicked.connect(self.load1act)
        self.load2.clicked.connect(self.load2act)
        self.grayImageLoad = np.zeros((240, 320), np.uint8)
        self.grayImageLoad2 = np.zeros((240, 320), np.uint8)
        self.imgLeftLoad = QImage(320, 240, QImage.Format_RGB888)
        self.imgRightLoad = QImage(320, 240, QImage.Format_RGB888)
        self.showMat.clicked.connect(self.showMatAction)
        #self.retranslateUi(MainWindow)
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.visorS.windowSelected.connect(self.selectWindow)
        self.visorS.pressEvent.connect(self.deSelectWindow)

########################### ORB TESTING ###############################
        self.orb = cv2.ORB_create()

    def load1act(self):
        imgPath, _ = QFileDialog.getOpenFileName()
        if imgPath != "":
            self.grayImageLoad = cv2.imread(imgPath)
            self.grayImageLoad = cv2.resize(self.grayImageLoad, (320,240))
            self.grayImageLoad = cv2.cvtColor(self.grayImageLoad, cv2.COLOR_BGR2GRAY)
        


    def load2act(self):
        imgPath, _ = QFileDialog.getOpenFileName()
        if imgPath != "":
            self.grayImageLoad2 = cv2.imread(imgPath)
            self.grayImageLoad2 = cv2.resize(self.grayImageLoad2, (320,240))
            self.grayImageLoad2 = cv2.cvtColor(self.grayImageLoad2, cv2.COLOR_BGR2GRAY)
        
    def showMatAction(self):
        print("Calculating...")
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(self.grayImageLoad, None)
        kp2, des2 = orb.detectAndCompute(self.grayImageLoad2, None)

        bf = cv2.BFMatcher()

        matches = bf.knnMatch(des1, des2, k = 2)

        good = []
        for m, n in matches:
            if m.distance < 0.95*n.distance:
                good.append([m])

        self.colorImageM = cv2.drawMatchesKnn(self.grayImageLoad, kp1, self.grayImageLoad2, kp2, good, None, flags=2)
        cv2.imwrite('prueba.png', self.colorImageM)
        self.colorImageM = cv2.resize(self.colorImageM, (700, 240))
        self.colorImageM = cv2.cvtColor(self.colorImageM, cv2.COLOR_BGR2RGB)

    def addAction(self):
        if len(self.objectList) != 3:
            self.addObject.show()
        else:
            message = QtWidgets.QMessageBox()
            message.about(None, 'Error', 'Error adding object: Maximum number of objects reached.')

    def addOkAction(self):
        #Add object to list
        self.addObject.hide()
        if self.actionReady is True:
            self.imageList.append()
            self.mapObjects[self.addObject.lineEdit.text()] = self.imageList[self.imageList[-1]]
            
    def renameAction(self):
        self.renameObject.show()

    def renameOkAction(self):
        self.renameObject.hide()

    def removeAction(self):
        item = self.objectList.itemData(self.objectList.currentIndex())
        self.objectList.removeItem(item)
        self.imageList.remove(item)

    def captureButtonAction(self):
        if self.captureState is False:
            self.captureButton.setChecked(True)
            self.captureButton.setText("Stop Capture")
            self.captureState = True
        else:
            self.captureState = False
            self.captureButton.setChecked(False)
            self.captureButton.setText("Start Capture")

    def selectWindow(self,  p, w, h):
        if w > 0 and h > 0:
            pEnd = QPointF()
            self.imageWindow.setX(p.x()-w / 2)
            if self.imageWindow.x() < 0:
                self.imageWindow.setX(0)
            self.imageWindow.setY(p.y()-h / 2)
            if self.imageWindow.y() < 0:
                self.imageWindow.setY(0)
            pEnd.setX(p.x()+w / 2)
            if pEnd.x() >= 320:
                pEnd.setX(319)
            pEnd.setY(p.y()+h / 2)
            if pEnd.y() >= 240:
                pEnd.setY(239)
            self.imageWindow.setWidth(pEnd.x()-self.imageWindow.x())
            self.imageWindow.setHeight(pEnd.y()-self.imageWindow.y())
            self.winSelected = True

    def deSelectWindow(self):
        self.winSelected = False
        self.actionReady = True

    def timerLoop(self):
        if (self.captureState == True and self.capture.isOpened() == True):
            ret, self.grayImage = self.capture.read()
            self.grayImage = cv2.resize(self.grayImage, (320, 240))
            self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)
            #print(self.grayImage.shape)
            kp = self.orb.detect(self.grayImage,None)
            kp, des = self.orb.compute(self.grayImage, kp)
            self.grayImageDest = copy.copy(self.grayImage)
            self.grayImageDest = cv2.drawKeypoints(self.grayImage, kp, self.grayImageDest, color= (255,255,255), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_OVER_OUTIMG)
        
        if self.winSelected:
            self.visorS.drawSquare(self.imageWindow, Qt.green)

        # FIXED: astype is needed to convert the cv type to the qt expected one
        self.visorS.set_open_cv_image(self.grayImage)
        # FIXED: astype is needed to convert the cv type to the qt expected one
        
        self.visorD.set_open_cv_image(self.grayImageDest)
        self.visorS.update()
        self.visorD.update()

        self.visorM.set_open_cv_imageColor(self.colorImageM)
        self.visorM.update()

    
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())