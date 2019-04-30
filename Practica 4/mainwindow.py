from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QLabel, QGraphicsScene
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtCore import QRect, QTimer, Qt, QLineF, QPointF
import cv2
from cv2 import VideoCapture
from matplotlib import pyplot as plt
import numpy as np
#from ImgViewer import ImgViewer
import copy
from ImgViewer import ImgViewer

class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui_MainWindow, self).__init__()

        ##################      UI loading      ##################

        #uic.loadUi('/Users/dakolas/Documents/GitHub/ArtificialVision/Practica 3/mainwindow.ui', self)
        uic.loadUi('Practica 4/mainwindow.ui', self)

        ##########################################################

        self.capture = VideoCapture(0)
        self.captureState = True
        self.captureButtonAction()

        self.imageWindow = QRect()

        self.winSelected = False
        self.actionReady = False
        self.openVideo = False
 
        #Timer to control the capture.
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerLoop)
        self.timer.start(16)
        
        ##################      Image arrays and viewer objects     ##################

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
        
        ##############################################################################


        ##################      Buttons     ##################

        self.captureButton.clicked.connect(self.captureButtonAction)
        self.loadButton.clicked.connect(self.loadAction)

        ######################################################

        
        ##############################################################

        self.edges = np.zeros((320, 240), np.int8)
        self.imgRegions = np.full((320, 240),-1, dtype = np.float32)
        self.listRegions = []
        
        ##############################################################

    def test(self):

        self.edges = cv2.Canny(self.grayImage,100,200)
        self.mask = cv2.copyMakeBorder(self.edges, 1,1,1,1, cv2.BORDER_CONSTANT, value = 255)

        plt.subplot(121),plt.imshow(self.grayImage,cmap = 'gray')
        plt.title('Original Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(122),plt.imshow(self.edges,cmap = 'gray')
        plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
        plt.show()

    '''
    What we have to do is fill each region with a value.
    Iterate over the whole image. If we find a point that doesn't have a region we call floodfill
    Floodfill will fill the region using the mask with a value and give us a rectangle. Using those,
    We iterate over that rectangle and add the points with that value to imgRegions, 
    so we don't iterate multiple times over the same region. After we have done that, we regenerate the mask
    to avoid having different regions with the same value.  
    '''
    def fillImgRegions(self):
        regionID = 0
        self.edges = cv2.Canny(self.grayImage,100,200)
        self.mask = cv2.copyMakeBorder(self.edges, 1,1,1,1, cv2.BORDER_CONSTANT, value = 255)
        for i in range (0, 320, 1):
            for j in range(0, 240, 1):
                if self.imgRegions[i][j] == -1 and self.edges[i][j] == 0:
                    retval, _, _, rect = cv2.floodFill(self.grayImage, self.mask, (i,j), 10)
                    for i in range (1, 240, 1):
                        for j in range(1, 320, 1):
                            if self.mask[i][j] == 10:
                                self.imgRegions[i][j] = regionID
                                regionID += 1
                                self.edges = cv2.Canny(self.grayImage,100,200)
                                self.mask = cv2.copyMakeBorder(self.edges, 1,1,1,1, cv2.BORDER_CONSTANT, value = 255)

        self.grayImageDest = self.imgRegions
        self.grayImageDest = cv2.resize(self.grayImageDest, (320, 240))
        #self.grayImageDest = cv2.cvtColor(self.grayImageDest, cv2.COLOR_BGR2GRAY)
        self.visorD.set_open_cv_image(self.grayImageDest)
        self.visorD.update()
    
    def loadAction(self):
        imgPath, _ = QFileDialog.getOpenFileName()
        
        if imgPath != "":
            self.grayImage = cv2.imread(imgPath)
            self.grayImage = cv2.resize(self.grayImage, (320, 240))
            self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)
        
        self.test()
        self.fillImgRegions()
        
    def captureButtonAction(self):
        if self.captureState is False:
            self.capture = VideoCapture(0)
            self.captureButton.setChecked(True)
            self.captureButton.setText("Stop Capture")
            self.captureState = True
            
        else:
            self.captureState = False
            self.captureButton.setChecked(False)
            self.captureButton.setText("Start Capture")

    def timerLoop(self):
        if (self.captureState == True and self.capture.isOpened() == True):
            ret, self.grayImage = self.capture.read()
            if ret is False:
                self.capture.release()
                self.captureState = False
                self.grayImage = np.zeros((240, 320), np.uint8)
                self.grayImageDest = np.zeros((240, 320), np.uint8)
                self.timer.stop()
                self.timer.start(16)
                return
            self.grayImage = cv2.resize(self.grayImage, (320, 240))
            self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)

        if self.winSelected:
            self.visorS.drawSquare(self.imageWindow, Qt.green)

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
