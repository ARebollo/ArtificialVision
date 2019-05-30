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

        uic.loadUi('mainwindow.ui', self)
        #uic.loadUi('Practica 5/mainwindow.ui', self)

        ##########################################################

        self.imageWindow = QRect()

        self.winSelected = False
        self.actionReady = False
        self.openVideo = False
        self.bothImg = False

        self.disparity = np.zeros((240, 320), np.uint8)
        self.timer = QTimer()
        self.timer.timeout.connect(self.propagateDisparity)

        ##################      Image arrays and viewer objects     ##################

        # FIXED: Opencv images where created with wrong width height values (switched) so the copy failed 
        # FIXED: original removed 2 of the 3 chanels with the np.zeros
        self.grayImage = np.zeros((240, 320), np.uint8)
        # self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)
        self.imgS = QImage(320, 240, QImage.Format_RGB888)
        self.visorS = ImgViewer(320, 240, self.imgS, self.imageFrameS)

        # FIXED: original removed 2 of the 3 chanels with the np.zeros

        self.grayImageDest = np.zeros((240,320), np.uint8)
        self.imgD = QImage(320, 240, QImage.Format_RGB888)
        self.visorD = ImgViewer(320, 240, self.imgD, self.imageFrameD)

        self.estimDispImg = np.zeros((240, 320), np.uint8)
        self.imgS_2 = QImage(320, 240, QImage.Format_RGB888)
        self.visorS_2 = ImgViewer(320, 240, self.imgS, self.imageFrameS_2)
        
        self.realDispImg = np.zeros((240,320), np.uint8)
        self.imgD_2 = QImage(320, 240, QImage.Format_RGB888)
        self.visorD_2 = ImgViewer(320, 240, self.imgD, self.imageFrameD_2)

        ##############################################################################


        ##################      Buttons     ##################

        self.loadButton_1.clicked.connect(self.loadAction)
        self.loadButton_2.clicked.connect(self.loadAction2)
        self.loadTruth_Button.clicked.connect(self.loadGroundTruth)
        self.initDisparity_button.clicked.connect(self.initializeDisparity)
        self.propDisparity_button.clicked.connect(self.propDispAction)
        #self.spinBoxDifference.valueChanged.connect(self.fillImgRegions)

        ######################################################

        
        ##############################################################

        self.edges = np.zeros((240, 320), np.int8)
        self.imgRegions = np.full((240, 320),-1, dtype = np.int32)
        self.listRegions = []
        self.origWidth = 0
        
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

        self.calculateDisparityCorners(threshArr, w)
        
        #Convert the boolean array into a black and white one
        #self.cornersImg = threshArr * np.full((240,320), 255 ,np.uint8)
        #self.visorS_2.set_open_cv_image(self.cornersImg)
        #self.visorS_2.update()

        #plt.subplot(121),plt.imshow(auxMatrix,cmap = 'gray')
        #plt.show()
        return threshArr

    def calculateDisparityCorners(self, threshArr, w):
        """
        Calculates the disparity value for the fixed points.
        For each of them, it tries to match a region of w points around the
        corner with the horizontal line at that height. When it finds them,
        it calculates the disparity value for the most likely point
        and sets it in the disparity array.
        """
        cornerSquare = np.full((240,320), np.bool_)
        method = cv2.TM_CCOEFF
        self.fixedPoints = np.zeros((320, 240))
        for i in range(240):
            for j in range(320):
                if threshArr[i][j] == True:
                    yl = i
                    xl = j
                    for k in range (-w, w, 1):
                        if(i+k >= 0 and i+k <240):
                            for l in range(-w, w, 1):
                                if (j+l >= 0 and j+l < 320):
                                    cornerSquare[k][l] = self.grayImage[i+k][j+l]
                    line, heightDiff = self.getEpipolarLine(w, yl)
                    #print("shapes: " , line.shape, cornerSquare.shape)
                    
                    if heightDiff < 0:
                        res = cv2.matchTemplate(line, cornerSquare[-heightDiff:], method)
                    else:
                        res = cv2.matchTemplate(line, cornerSquare, method)
                    #TODO: Check if max_val is good
                    min_val, max_val, minLoc , maxLoc = cv2.minMaxLoc(res)
                    self.fixedPoints[i][j] = True
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
        if yl-w < 0:
            return self.grayImageDest[0:yl+w + 1], yl-w
        elif yl+w >= 240:
            return self.grayImageDest[yl-w:239], yl-w
        else:
            return self.grayImageDest[yl-w:yl+w + 1], yl-w

    def calculateRegions(self):

        regionID = 0
        self.listRegions.clear()

        edges = cv2.Canny(self.grayImage,40,120)
        mask = cv2.copyMakeBorder(edges, 1,1,1,1, cv2.BORDER_CONSTANT, value = 255)

        floodFlags = cv2.FLOODFILL_MASK_ONLY | 4 | cv2.FLOODFILL_FIXED_RANGE | 1 << 8

        for i in range(0, 240, 1):
            for j in range(0, 320, 1):
                #We found a new region:
                
                if self.imgRegions[i][j] == -1 and self.edges[i][j] == 0: #Optimize this, it's the part that makes it stupid slow
                    
                    _, _, newMask, rect = cv2.floodFill(self.grayImage, mask, (j,i), 1, loDiff = 40, 
                    upDiff = 40, flags = floodFlags)
                    
                    newRegion = region(regionID, rect)

                    for k in range (rect[0], rect[0] + rect[2], 1):
                        for l in range(rect[1], rect[1] + rect[3], 1):
                            if newMask[l+1][k+1] == 1 and self.imgRegions[l][k] == -1:
                                self.imgRegions[l][k] = regionID
                                    
                        
                    self.listRegions.append(copy.deepcopy(newRegion))

                    regionID += 1
                    #self.mask = cv2.copyMakeBorder(self.edges, 1,1,1,1, cv2.BORDER_CONSTANT, value = 255)

    def initializeDisparity(self):
        for i in self.listRegions:
            average = 0
            count = 0
            rect = i.rect
            id = i.id
            for j in range (rect[0], rect[0] + rect[2], 1):
                for k in range(rect[1], rect[1] + rect[3], 1):
                    if self.imgRegions[j][k] == id:  
                        average += self.disparity[j][k]
                        count += 1
            averageRegion = int(average/count)
            for j in range (rect[0], rect[0] + rect[2], 1):
                for k in range(rect[1], rect[1] + rect[3], 1):
                    if self.imgRegions[j][k] == id and self.disparity[j][k] == 0:
                        self.disparity[j][k] = averageRegion
                        
    def propDispAction(self):
        if self.propDisparity_button.isChecked() is True:
            self.timer.stop()
            self.propDisparity_button.setChecked(False)
        else: 
            self.timer.start(100)
            self.propDisparity_button.setChecked(True)

    def propagateDisparity(self, envWidth):
        for i in range(240):
            for j in range(320):
                if self.fixedPoints[i][j] == False: #To avoid changing fixed points
                    avgDisp = 0
                    count = 0
                    origRegion = self.imgRegions[i][j]
                    for k in range(-envWidth,envWidth+1,1):
                        if (i+k >= 0 and i+k <240):
                            for l in range(-envWidth,envWidth+1,1):
                                if (j+l >= 0 and j+l <320):
                                    #To avoid taking into account the point itself or adding points from other regions
                                    if (k == 0 and l == 0) == False or self.imgRegions[i+k][j+l] != origRegion: 
                                        avgDisp += self.disparity[i+k][j+l]
                                        count += 1
                    self.disparity[i][j] = int(avgDisp/count)

        pass

    def showDisparity(self):
        for i in range(240):
            for j in range(320):
                value = 3*self.disparity[i][j]*self.origWidth/320
                if value > 255:
                    value = 255
                self.estimDispImg[i][j] = value
        pass

    def loadAction(self):
        imgPath, _ = QFileDialog.getOpenFileName()
        
        if imgPath != "":
            self.grayImage = cv2.imread(imgPath)
            self.origWidth = self.grayImage.shape[1]
            self.grayImage = cv2.resize(self.grayImage, (320, 240))
            self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)
            if self.bothImg == True:
                self.calculateCorners(5)
            else:
                self.bothImg = True
            self.visorS.set_open_cv_image(self.grayImage)
            self.visorS.update()

    def loadAction2(self):
        imgPath, _ = QFileDialog.getOpenFileName()
        
        if imgPath != "":
            self.grayImageDest = cv2.imread(imgPath)
            self.grayImageDest = cv2.resize(self.grayImageDest, (320, 240))
            self.grayImageDest = cv2.cvtColor(self.grayImageDest, cv2.COLOR_BGR2GRAY)
            self.visorD.set_open_cv_image(self.grayImageDest)
            if self.bothImg == True:
                self.calculateCorners(5)
            else:
                self.bothImg = True
            self.visorD.update()
    
    def loadGroundTruth(self):
        pass
               
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())
