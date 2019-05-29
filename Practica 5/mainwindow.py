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
from region import region
from regionColor import regionColor

class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui_MainWindow, self).__init__()

        ##################      UI loading      ##################

        #uic.loadUi('mainwindow.ui', self)
        uic.loadUi('Practica 5/mainwindow.ui', self)

        ##########################################################

        self.capture = VideoCapture(0)
        self.captureState = True
        self.captureButtonAction()
        self.colorState = False
        self.imageWindow = QRect()

        self.winSelected = False
        self.actionReady = False
        self.openVideo = False
        self.bothImg = False

        self.disparity = np.zeros((240, 320), np.uint8)
       
        ##################      Image arrays and viewer objects     ##################

        # FIXED: Opencv images where created with wrong width height values (switched) so the copy failed 
        # FIXED: original removed 2 of the 3 chanels with the np.zeros
        self.grayImage = np.zeros((240, 320), np.uint8)
        self.colorImage = np.zeros((240,320,3), np.uint8)
        # self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)
        self.imgS = QImage(320, 240, QImage.Format_RGB888)
        self.visorS = ImgViewer(320, 240, self.imgS, self.imageFrameS)

        # FIXED: original removed 2 of the 3 chanels with the np.zeros

        self.grayImageDest = np.zeros((240,320), np.uint8)
        self.colorImageDest = np.zeros((240,320,3), np.uint8)
        self.imgD = QImage(320, 240, QImage.Format_RGB888)
        self.visorD = ImgViewer(320, 240, self.imgD, self.imageFrameD)

        self.cornersImg = np.zeros((240, 320), np.uint8)
        self.imgS_2 = QImage(320, 240, QImage.Format_RGB888)
        self.visorS_2 = ImgViewer(320, 240, self.imgS, self.imageFrameS_2)
        
        ##############################################################################


        ##################      Buttons     ##################

        self.colorButton.clicked.connect(self.colorButtonAction)
        self.loadButton_1.clicked.connect(self.loadAction)
        self.loadButton_2.clicked.connect(self.loadAction2)
        #self.spinBoxDifference.valueChanged.connect(self.fillImgRegions)

        ######################################################

        
        ##############################################################

        self.edges = np.zeros((240, 320), np.int8)
        self.imgRegions = np.full((240, 320),-1, dtype = np.int32)
        self.listRegions = []
        
        ##############################################################

    '''
    What we have to do is fill each region with a value.
    Iterate over the whole image. If we find a point that doesn't have a region we call floodfill
    Floodfill will fill the region using the mask with a value and give us a rectangle. Using those,
    We iterate over that rectangle and add the points with that value to imgRegions, 
    so we don't iterate multiple times over the same region. After we have done that, we regenerate the mask
    to avoid having different regions with the same value.  
    '''
    
    def calculateCorners(self, w):
        
        if self.colorState == True:
            dst = cv2.cornerHarris(self.grayImage, 2, 3, 0.04)
        else:
            dst = cv2.cornerHarris(self.colorImage, 2, 3, 0.04)
        
        threshArr = (dst > 1e-5)
        
        for i in range(240):
            for j in range(320):
                if threshArr[i][j] == True:
                    for k in range (-2, 3, 1):
                        if(i+k >= 0 and i+k <240):
                            for l in range(-2, 3, 1):
                                if (j+l >= 0 and j+l < 320):
                                    if(threshArr[i+k][j+l] == True):
                                        threshArr[i+k][j+l] = False
                    threshArr[i][j] = True
        self.calculateDisparity(threshArr, w)
        
        '''
        auxMatrix = np.zeros((240,320), np.uint8)

        for i in range(240):
            for j in range(320):
                if threshArr[i][j] == True:
                    if(i+k >= 0 and i+k <240):
                        if (j+l >= 0 and j+l < 320):
                            auxMatrix[i][j] = True
                            
                            for k in range (1, 2, 1):
                                auxMatrix[i-k][j-k] = True
                                auxMatrix[i-k][j+k] = True
                                auxMatrix[i+k][j-k] = True
                                auxMatrix[i+k][j+k] = True
        '''
        
        self.cornersImg = threshArr * np.full((240,320), 255 ,np.uint8)
        self.visorS_2.set_open_cv_image(self.cornersImg)
        self.visorS_2.update()

        #plt.subplot(121),plt.imshow(auxMatrix,cmap = 'gray')
        #plt.show()
        return threshArr

    def calculateDisparity(self, threshArr, w):

        cornerSquare = np.zeros((w,w), np.uint8)
        method = cv2.TM_CCOEFF

        for i in range(240):
            for j in range(320):
                if threshArr[i][j] == True:
                    yl = i
                    xl = j
                    for k in range (int(-w/2), int(w/2), 1):
                        if(i+k >= 0 and i+k <240):
                            for l in range(int(-w/2), int(w/2), 1):
                                if (j+l >= 0 and j+l < 320):
                                    cornerSquare[k][l] = self.grayImage[i+k][j+l]
                    line, heightDiff = self.getEpipolarLine(w, yl)
                    #print("shapes: " , line.shape, cornerSquare.shape)
                    
                    if heightDiff < 0:
                        res = cv2.matchTemplate(line, cornerSquare[-heightDiff:], method)
                    else:
                        res = cv2.matchTemplate(line, cornerSquare, method)

                    min_val, max_val, minLoc , maxLoc = cv2.minMaxLoc(res)
    
                    self.disparity[i][j] = xl - maxLoc[0]

                    '''
                    print("Minimum value: ", str(min_val))
                    print("Maximum value: ", str(max_val))
                    print("Minimum location: ", str(minLoc))
                    print("Maximum location: ", str(maxLoc))
                    '''
        for x in self.disparity:
            print(x, end='')

    def getEpipolarLine(self, w, yl):
        if int(yl-w/2) < 0:
            return self.grayImageDest[0:yl+int(w/2 + 1)], int(yl-w/2)
        elif int(yl+w/2) >= 240:
            return self.grayImageDest[yl-int(w/2):239], int(yl-w/2)
        else:
            return self.grayImageDest[yl-int(w/2):yl+int(w/2 + 1)], int(yl-w/2)

    def fillImgRegions(self):

        regionID = 1
        regionList = []
  
        self.edges = cv2.Canny(self.grayImage,40,120)
        
        self.mask = cv2.copyMakeBorder(self.edges, 1,1,1,1, cv2.BORDER_CONSTANT, value = 255)

        dialogValue = self.spinBoxDifference.value()
        if self.checkBoxRange.isChecked() is True:
            floodFlags = cv2.FLOODFILL_MASK_ONLY | 4 | 1 << 8
        else:
            floodFlags = cv2.FLOODFILL_MASK_ONLY | 4 | cv2.FLOODFILL_FIXED_RANGE | 1 << 8

        for i in range(0, 240, 1):
            for j in range(0, 320, 1):
                #We found a new region:
                
                if self.imgRegions[i][j] == -1: #Optimize this, it's the part that makes it stupid slow
                    if self.edges[i][j] == 0:
                    
                        _, _, newMask, rect = cv2.floodFill(self.grayImage, self.mask, (j,i), 1, loDiff = dialogValue, 
                        upDiff = dialogValue, flags = floodFlags)
                    
                        newRegion = region(regionID, rect)

                        for k in range (rect[0], rect[0] + rect[2], 1):
                            for l in range(rect[1], rect[1] + rect[3], 1):
                                if newMask[l+1][k+1] == 1 and self.imgRegions[l][k] == -1:
                                    self.imgRegions[l][k] = regionID
                                    newRegion.addPoint(self.grayImage[l][k])
                        newRegion.calcAverage()
                        regionList.append(newRegion)

                        regionID += 1
                    #self.mask = cv2.copyMakeBorder(self.edges, 1,1,1,1, cv2.BORDER_CONSTANT, value = 255)
        
        for i in range(240):
            for j in range(320):
                if self.imgRegions[i][j] != -1:
                    regionIndex = self.imgRegions[i][j] -1
                    region2 = regionList[regionIndex]
                    avgGrey = region2.returnAverage()
                    self.grayImageDest[i][j] = avgGrey

        checkBreak = False
        if self.checkBoxBorders.isChecked() is True:
            #We skip the first to avoid out of bounds. Can be done manually, or adding an if check that makes everything slow as fuck.
            for i in range(1, 240, 1):
                for j in range(1, 320, 1):
                    checkBreak = False
                    for k in range(1, -2, -1):
                        if checkBreak is True:
                            break
                        for l in range(1, -2, -1):
                            if self.imgRegions[i][j] != self.imgRegions[i+k][j+l]:
                                self.grayImageDest[i][j] = 255
                                checkBreak = True
                                break

        self.visorD.set_open_cv_image(self.grayImageDest)
        self.visorD.update()
        self.imgRegions = np.full((240, 320),-1, dtype = np.int32)
        
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
    
    def loadAction(self):
        imgPath, _ = QFileDialog.getOpenFileName()
        
        if imgPath != "":
            if self.colorState is True:
                self.grayImage = cv2.imread(imgPath)
                self.grayImage = cv2.resize(self.grayImage, (320, 240))
                self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)
                if self.bothImg == True:
                    self.calculateCorners(11)
                self.visorS.set_open_cv_image(self.grayImage)

            else:
                self.colorImage = cv2.imread(imgPath)
                self.colorImage = cv2.resize(self.colorImage, (320, 240))
                self.colorImage = cv2.cvtColor(self.colorImage, cv2.COLOR_BGR2GRAY)
                if self.bothImg == True:
                    self.calculateCorners(11)
                self.visorS.set_open_cv_image(self.colorImage)
        self.visorS.update()

    def loadAction2(self):
        imgPath, _ = QFileDialog.getOpenFileName()
        
        if imgPath != "":
            if self.colorState is True:
                self.grayImageDest = cv2.imread(imgPath)
                self.grayImageDest = cv2.resize(self.grayImageDest, (320, 240))
                self.grayImageDest = cv2.cvtColor(self.grayImageDest, cv2.COLOR_BGR2GRAY)
                self.visorD.set_open_cv_image(self.grayImageDest)
                self.bothImg = True
            else:
                self.colorImageDest = cv2.imread(imgPath)
                self.colorImageDest = cv2.resize(self.colorImageDest, (320, 240))
                self.colorImageDest = cv2.cvtColor(self.colorImageDest, cv2.COLOR_BGR2GRAY)
                self.visorD.set_open_cv_image(self.colorImageDest)
                self.bothImg = True
                
        self.visorD.update()

        
    def captureButtonAction(self):
        if self.captureState is False:
            self.capture = VideoCapture(0)
            self.captureButton.setChecked(True)
            self.captureButton.setText("Stop Capture")
            self.captureState = True
        else:
            self.captureState = False
               
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())
