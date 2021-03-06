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
import math

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

        self.disparity = np.zeros((240, 320), np.float32)
        #self.timer = QTimer()
        #self.timer.timeout.connect(self.timerExpired)

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
        self.visorS_2.windowSelected.connect(self.dispClick)
        #self.spinBoxDifference.valueChanged.connect(self.fillImgRegions)
        self.checkBoxRange.stateChanged.connect(self.checkBoxAction)
        self.kernelSpinBox.valueChanged.connect(self.kernelAction)
        self.iterationSpinBox.valueChanged.connect(self.iterationAction)
        self.kernel = 0
        self.iterations = 0
        self.goodCorners = []
        self.notSoGoodCorners = []

        ######################################################
        
        ##############################################################

        self.edges = np.zeros((240, 320), np.int8)
        self.imgRegions = np.full((240, 320),-1, dtype = np.int32)
        self.listRegions = []
        self.origWidth = 0
        self.fixedPoints = np.zeros((240, 320), dtype = bool)
        self.shiftedPoints = np.zeros((240, 320), dtype = bool)

        ##############################################################

    '''
    What we have to do is fill each region with a value.
    Iterate over the whole image. If we find a point that doesn't have a region we call floodfill
    Floodfill will fill the region using the mask with a value and give us a rectangle. Using those,
    We iterate over that rectangle and add the points with that value to imgRegions, 
    so we don't iterate multiple times over the same region. After we have done that, we regenerate the mask
    to avoid having different regions with the same value.  
    '''
    
    def kernelAction(self):
        self.kernel = self.kernelSpinBox.value()
        print("kernel: " , self.kernel)
    def iterationAction(self):
        self.iterations = self.iterationSpinBox.value()
        print("iterations: " , self.iterations)

    def checkBoxAction(self):
        if self.checkBoxRange.isChecked():
            self.showCorners()

    def showCorners(self):
        auxImg = cv2.cvtColor(self.grayImage, cv2.COLOR_GRAY2RGB)
        auxImg2 = cv2.cvtColor(self.grayImageDest, cv2.COLOR_GRAY2RGB)
        
        auxCorners = self.calculateCorners(5)
        unMatchedCorners = np.zeros((240, 320), np.uint8)

        green = [39, 225, 20]
        red = [207, 4, 44]

        print("shape"+ str(auxCorners.shape))

        for i in range(1,239,1):
            for j in range(1,319,1):
                if auxCorners[i][j] == True and self.fixedPoints[i][j] == False:
                    unMatchedCorners[i][j] = True
                else:
                    unMatchedCorners[i][j] = False

        for i in range(1,237,1):
            for j in range(1,317,1):
                if self.fixedPoints[i][j] == True:
                    auxImg[i][j] = green
                    for k in range(0,4):
                        auxImg[i-k][j-k] = green
                        auxImg[i+k][j+k] = green
                        auxImg[i-k][j+k] = green
                        auxImg[i+k][j-k] = green
                if unMatchedCorners[i][j] == True:
                    auxImg[i][j] = red
                    for k in range(0,4):
                        auxImg[i-k][j-k] = red
                        auxImg[i+k][j+k] = red
                        auxImg[i-k][j+k] = red
                        auxImg[i+k][j-k] = red

        for i in range(1,237,1):
            for j in range(1,317,1):
                if self.shiftedPoints[i][j] == True:
                    auxImg2[i][j] = green
                    for k in range(0,4):
                        auxImg2[i-k][j-k] = green
                        auxImg2[i+k][j+k] = green
                        auxImg2[i-k][j+k] = green
                        auxImg2[i+k][j-k] = green
                        
        #cv2.imshow('img', auxImg)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        #plt.subplot(121),plt.imshow(auxCorners,cmap = 'gray')
        #plt.show()

        self.visorS.set_open_cv_image(auxImg)
        self.visorS.update()
        self.visorD.set_open_cv_image(auxImg2)
        self.visorD.update()


    def calculateCorners(self, w):
        
        dst = cv2.cornerHarris(self.grayImage, 3, 3, 0.04)
        
        self.notSoGoodCorners = dst

        threshArr = (dst > 1e-6)
        #threshArr = (dst > 1e-6)
        
        #List of good corners. Contains HarrisValue, i, j, Deleted.
        cornerList = [] 
        for i in range(240):
            for j in range(320):
                if threshArr[i][j] == True:
                    cornerList.append([dst[i][j], i, j, False])
        #cornerList.sort(key = lambda x: x[0], reverse = True)
        cornerList = sorted(cornerList, reverse = True, key=lambda x: x[0])
        for i in range(len(cornerList)): 
            if cornerList[i][3]==False:
                for j in range(i+1, len(cornerList), 1):
                    if cornerList[j][3]==False:
                        XdistSq = (cornerList[i][1]-cornerList[j][1]) ** 2
                        YdistSq = (cornerList[i][2]-cornerList[j][2]) ** 2
                        dist = math.sqrt(XdistSq+YdistSq)
                        if dist < 3:
                            cornerList[j][3] = True

        for corner in cornerList:
            if corner[3]==True:
                threshArr[corner[1]][corner[2]] = False
        #self.goodCorners = copy.deepcopy(dst)
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
        cornerSquare = np.zeros((2*w+1,2*w+1), dtype=np.uint8)
        method = cv2.TM_CCOEFF_NORMED
        
        for i in range(5,235,1):
            for j in range(5,315,1):
                if threshArr[i][j] == True:
                    yl = i 
                    xl = j
                    for k in range (-w, w+1, 1):
                        if(i+k >= 0 and i+k <240):
                            for l in range(-w, w+1, 1):
                                if (j+l >= 0 and j+l < 320):
                                    cornerSquare[w+k][w+l] = self.grayImage[i+k][j+l]
                    line, heightDiff = self.getEpipolarLine(w, yl)
                    #print("shapes: " , line.shape, cornerSquare.shape)
                    if heightDiff >= 0:
                        res = cv2.matchTemplate(line, cornerSquare, method)
                        
                        #TODO: Check if max_val is good
                        min_val, max_val, minLoc , maxLoc = cv2.minMaxLoc(res)
                        #print("TEST", maxLoc)
                        if (max_val > 0.95):
                            self.fixedPoints[i][j] = True
                            self.disparity[i][j] = xl - (maxLoc[0] + w)

        for i in range(1,239,1):
            for j in range(1,319,1):
                if self.fixedPoints[i][j] == True:
                    shift = self.disparity[i][j]
                    self.shiftedPoints[i][j-int(shift)] = self.fixedPoints[i][j]
                        
                    '''
                    print("Minimum value: ", str(min_val))
                    print("Maximum value: ", str(max_val))
                    print("Minimum location: ", str(minLoc))
                    print("Maximum location: ", str(maxLoc))
                    '''
        if self.checkBoxCorners.isChecked() == True:
            rightCorners = self.calculateGoodCornersRight(w)
            self.shiftedPoints = np.logical_and(self.shiftedPoints, rightCorners)
            
                    
        
        return threshArr

    def calculateGoodCornersRight(self, w):

        dst = cv2.cornerHarris(self.grayImageDest, 3, 3, 0.04)


        threshArr = (dst > 1e-6)
        #threshArr = (dst > 1e-6)
        
        #List of good corners. Contains HarrisValue, i, j, Deleted.
        cornerList = [] 
        for i in range(240):
            for j in range(320):
                if threshArr[i][j] == True:
                    cornerList.append([dst[i][j], i, j, False])
        #cornerList.sort(key = lambda x: x[0], reverse = True)
        cornerList = sorted(cornerList, reverse = True, key=lambda x: x[0])
        for i in range(len(cornerList)): 
            if cornerList[i][3]==False:
                for j in range(i+1, len(cornerList), 1):
                    if cornerList[j][3]==False:
                        XdistSq = (cornerList[i][1]-cornerList[j][1]) ** 2
                        YdistSq = (cornerList[i][2]-cornerList[j][2]) ** 2
                        dist = math.sqrt(XdistSq+YdistSq)
                        if dist < 3:
                            cornerList[j][3] = True

        for corner in cornerList:
            if corner[3]==True:
                threshArr[corner[1]][corner[2]] = False
        #self.goodCorners = copy.deepcopy(dst)

        cornerSquare = np.zeros((2*w+1,2*w+1), dtype=np.uint8)
        method = cv2.TM_CCOEFF_NORMED
        rightCorners = np.full((240,320), False, dtype = bool)
        rightDisp = np.full((240, 320), 0.0, dtype = np.float32)
        for i in range(5,235,1):
            for j in range(5,315,1):
                if threshArr[i][j] == True:
                    yl = i 
                    xl = j
                    for k in range (-w, w+1, 1):
                        if(i+k >= 0 and i+k <240):
                            for l in range(-w, w+1, 1):
                                if (j+l >= 0 and j+l < 320):
                                    cornerSquare[w+k][w+l] = self.grayImageDest[i+k][j+l]
                    line, heightDiff = self.getEpipolarLine(w, yl)
                    #print("shapes: " , line.shape, cornerSquare.shape)
                    if heightDiff >= 0:
                        res = cv2.matchTemplate(line, cornerSquare, method)
                        
                        #TODO: Check if max_val is good
                        min_val, max_val, minLoc , maxLoc = cv2.minMaxLoc(res)
                        #print("TEST", maxLoc)
                        if (max_val > 0.95):
                            rightCorners[i][j] = True
                            rightDisp[i][j] = xl - (maxLoc[0] + w)
        

        return rightCorners
        

    def getEpipolarLine(self, w, yl):
        if yl-w < 0:
            return self.grayImageDest[0:yl+w + 1], yl-w
        elif yl+w >= 240:
            return self.grayImageDest[yl-w:239], yl-w
        else:
            return self.grayImageDest[yl-w:yl+w + 1], yl-w

    def calculateDiff(self):

        count = 0
        percentDiff = 0.0
        for i in range(240):
            for j in range(320):
                if self.estimDispImg[i][j] != 0:
                      count += 1
                      percentDiff += abs(self.realDispImg[i][j]-self.estimDispImg[i][j])/255.0

        self.dispPerc.display(percentDiff/count)

    def fillImgRegions(self):

        regionID = 1
        
        self.edges = cv2.Canny(self.grayImage,40,120)
        
        self.mask = cv2.copyMakeBorder(self.edges, 1,1,1,1, cv2.BORDER_CONSTANT, value = 255)
        floodFlags = cv2.FLOODFILL_MASK_ONLY | 4 | 1 << 8
        
        for i in range(0, 240, 1):
            for j in range(0, 320, 1):
                #We found a new region:
                
                if self.imgRegions[i][j] == -1: #Optimize this, it's the part that makes it stupid slow
                    if self.edges[i][j] == 0:
                    
                        _, _, newMask, rect = cv2.floodFill(self.grayImage, self.mask, (j,i), 1, loDiff = 10, 
                        upDiff = 10, flags = floodFlags)
                    
                        newRegion = region(regionID, rect)

                        for k in range (rect[0], rect[0] + rect[2], 1):
                            for l in range(rect[1], rect[1] + rect[3], 1):
                                if newMask[l+1][k+1] == 1 and self.imgRegions[l][k] == -1:
                                    self.imgRegions[l][k] = regionID
                        
                        self.listRegions.append(copy.deepcopy(newRegion))

                        regionID += 1
                    #self.mask = cv2.copyMakeBorder(self.edges, 1,1,1,1, cv2.BORDER_CONSTANT, value = 255)
        
        for i in range(1,239,1):
            for j in range(1,319,1):
                if self.imgRegions[i][j] == -1:
                    for k in range(-1,2,1):
                        for l in range(-1,2,1):
                            if self.imgRegions[i+k][j+l] != -1 and self.imgRegions[i][j] == -1:
                                self.imgRegions[i][j] = self.imgRegions[i+k][j+l]
        
        #plt.subplot(121),plt.imshow(self.imgRegions,cmap = 'gray')
        #plt.show()   
        #self.visorD.set_open_cv_image(self.grayImageDest)
        #self.visorD.update()
        #self.imgRegions = np.full((240, 320), -1, dtype=np.int32)

    def initializeDisparity(self):

        self.calculateCorners(5)
        
        self.fillImgRegions()   
        #print(len(self.listRegions))
        for i in range(240):
            for j in range(320):
                if self.disparity[i][j] != 0:
                    #print(self.imgRegions[i][j]-1)
                    region = self.listRegions[self.imgRegions[i][j]-1]
                    region.addPoint(self.disparity[i][j])
                    #self.listRegions[self.imgRegions[i][j]-1].addPoint(self.disparity[i][j])
        
        for i in self.listRegions:
            i.calcAverage()
        #print(np.amax(self.imgRegions))
        for i in range(240):
            for j in range(320):
                if self.disparity[i][j] == 0:
                    #print("max reg = ", len(self.listRegions), " index= ", self.imgRegions[i][j])
                    self.disparity[i][j] = self.listRegions[self.imgRegions[i][j]-1].returnAverage()
        
        self.showDisparity()
        self.calculateDiff()

    def propDispAction(self):

        for i in range(self.iterations):
            self.propagateDisparity(self.kernel)


        self.showDisparity()
        self.calculateDiff()
    '''
    def timerExpired(self):
        self.propagateDisparity(1)
    '''

    def propagateDisparity(self, envWidth):
        
        '''
        contTrue = 0
        contFalse = 0

        for i in range(1,240,1):
            for j in range(1,320,1):
                if self.fixedPoints[i][j] == True:
                    contTrue += 1
                else:
                    contFalse += 1

        print("contTrue: " , contTrue)
        print("contFalse: " , contFalse)
        '''
        
        for i in range(envWidth, 240-envWidth):
            for j in range(envWidth, 320-envWidth):
                if self.fixedPoints[i][j] == False: #To avoid changing fixed points
                    avgDisp = 0.0
                    count = 0
                    origRegion = self.imgRegions[i][j]
                    #todo cambiar
                    for k in range(-envWidth,envWidth+1,1):
                        #todo cambiar
                        for l in range(-envWidth,envWidth+1,1):
                            #To avoid taking into account the point itself or adding points from other regions
                            if self.imgRegions[i+k][j+l] == origRegion: 
                                #print("origRegion")
                                avgDisp += self.disparity[i+k][j+l]
                                count += 1
                    if count != 0:
                        self.disparity[i][j] = float(avgDisp/count)
                        #print("disparity i,j: " , i , j , self.disparity[i][j])
        

    def showDisparity(self):
        for i in range(240):
            for j in range(320):
                value = 3*self.disparity[i][j]*self.origWidth/320
                if value > 255:
                    value = 255
                self.estimDispImg[i][j] = value
        
        self.visorS_2.set_open_cv_image(cv2.cvtColor(self.estimDispImg, cv2.COLOR_GRAY2RGB))
        self.visorS_2.update()

    def dispClick(self, point, posX, posY):
        X = int(point.x() - posX/2)
        if X < 0: 
            X = 0
        Y = int(point.y()-posY/2)
        if Y < 0:
            Y = 0
        #print(self.disparity[Y][X])
        #print(self.estimDispImg[Y][X])
        self.estimatedDisp.display(self.estimDispImg[Y][X])
        self.trueDisp.display(self.realDispImg[Y][X])

    def loadAction(self):
        imgPath, _ = QFileDialog.getOpenFileName()
        
        if imgPath != "":
            self.grayImage = cv2.imread(imgPath)
            self.origWidth = self.grayImage.shape[1]
            self.grayImage = cv2.resize(self.grayImage, (320, 240))
            self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)
            
                
            
            self.visorS.set_open_cv_image(cv2.cvtColor(self.grayImage, cv2.COLOR_GRAY2RGB))
            self.visorS.update()

    def loadAction2(self):
        imgPath, _ = QFileDialog.getOpenFileName()
        
        if imgPath != "":
            self.grayImageDest = cv2.imread(imgPath)
            self.grayImageDest = cv2.resize(self.grayImageDest, (320, 240))
            self.grayImageDest = cv2.cvtColor(self.grayImageDest, cv2.COLOR_BGR2GRAY)
            
            self.visorD.set_open_cv_image(cv2.cvtColor(self.grayImageDest, cv2.COLOR_GRAY2RGB))
            
            self.visorD.update()
    
    def loadGroundTruth(self):
        imgPath, _ = QFileDialog.getOpenFileName()
    
        if imgPath != "":
            self.realDispImg = cv2.imread(imgPath)
            self.realDispImg = cv2.resize(self.realDispImg, (320, 240))
            self.realDispImg = cv2.cvtColor(self.realDispImg, cv2.COLOR_BGR2GRAY)
            self.visorD_2.set_open_cv_image(cv2.cvtColor(self.realDispImg, cv2.COLOR_GRAY2RGB))
               
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())
