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

        self.renameObject =  QtWidgets.QDialog()
        uic.loadUi('objectRename.ui', self.renameObject)
        self.renameObject.okButton.clicked.connect(self.renameOkAction)

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
        self.renameButton.clicked.connect(self.renameAction)
        self.removeButton.clicked.connect(self.removeAction)


        self.load1.clicked.connect(self.load1act)
        self.load2.clicked.connect(self.load2act)
        self.grayImageLoad = np.zeros((240, 320), np.uint8)
        self.grayImageLoad2 = np.zeros((240, 320), np.uint8)
        self.imgLeftLoad = QImage(320, 240, QImage.Format_RGB888)
        self.imgRightLoad = QImage(320, 240, QImage.Format_RGB888)
        self.showMat.clicked.connect(self.showMatAction)
        #self.retranslateUi(MainWindow)
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

########################### ORB TESTING ###############################
        self.orb = cv2.ORB_create()


    def load1act(self):
        imgPath, _ = QFileDialog.getOpenFileName()
        self.grayImageLoad = cv2.imread(imgPath)
        self.grayImageLoad = cv2.resize(self.grayImageLoad, (320,240))
        self.grayImageLoad = cv2.cvtColor(self.grayImageLoad, cv2.COLOR_BGR2GRAY)
        


    def load2act(self):
        imgPath, _ = QFileDialog.getOpenFileName()
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

        result = cv2.drawMatchesKnn(self.grayImageLoad, kp1, self.grayImageLoad2, kp2, good, None, flags=2)
        cv2.imwrite('ResultImage.png', result)
        
        #self.grayImageDest = cv2.resize(self.grayImageDest, (320, 240))
        #label = QLabel(self.imageFrameS_2)5
        #imgMat = QImage(img3, img3.shape[1], img3.shape[0],                                                                                                                                                 
                         #QImage.Format_Grayscale8)
        

        #label.setPixmap(QPixmap.fromImage(imgMat))
        
        

    def addAction(self):
        if self.objectList.count() is not 3:
            self.addObject.show()
        else:
            message = QtWidgets.QMessageBox()
            message.about(None, 'Error', 'Error adding object: Maximum number of objects reached.')

    def addOkAction(self):
        #Add object to list
        self.addObject.hide()
        pass

    def renameAction(self):
        self.renameObject.show()

    def renameOkAction(self):
        self.renameObject.hide()

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
            #print(self.grayImage.shape)
            kp = self.orb.detect(self.grayImage,None)
            kp, des = self.orb.compute(self.grayImage, kp)
            self.grayImageDest = copy.copy(self.grayImage)
            self.grayImageDest = cv2.drawKeypoints(self.grayImage, kp, self.grayImageDest, color= (255,255,255), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_OVER_OUTIMG)
            print (self.grayImageDest.shape)
            #self.grayImageDest = copy.copy(self.grayImage)



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