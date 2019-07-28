from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QLabel, QGraphicsScene
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtCore import QRect, QTimer, Qt, QLineF, QPointF
import cv2
from cv2 import VideoCapture
from matplotlib import pyplot as plt
import numpy as np
from distutils.core import setup 
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
        uic.loadUi('Practica 4/mainwindow.ui', self)

        ##########################################################

        self.capture = VideoCapture(0)
        self.captureState = True
        self.captureButtonAction()
        self.colorState = False
        self.imageWindow = QRect()

        self.winSelected = False
        self.actionReady = False
        self.openVideo = False

        # Timer to control the capture.
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerLoop)
        self.timer.start(16)

        ##################      Image arrays and viewer objects     ##################

        # FIXED: Opencv images where created with wrong width height values (switched) so the copy failed
        # FIXED: original removed 2 of the 3 chanels with the np.zeros
        self.grayImage = np.zeros((240, 320), np.uint8)
        self.colorImage = np.zeros((240, 320, 3), np.uint8)
        # self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)
        self.imgS = QImage(320, 240, QImage.Format_RGB888)
        self.visorS = ImgViewer(320, 240, self.imgS, self.imageFrameS)

        # FIXED: original removed 2 of the 3 chanels with the np.zeros

        self.grayImageDest = np.zeros((240, 320), np.uint8)
        self.colorImageDest = np.zeros((240, 320, 3), np.uint8)
        self.imgD = QImage(320, 240, QImage.Format_RGB888)
        self.visorD = ImgViewer(320, 240, self.imgD, self.imageFrameD)

        ##############################################################################

        ##################      Buttons     ##################

        self.colorButton.clicked.connect(self.colorButtonAction)
        self.captureButton.clicked.connect(self.captureButtonAction)
        self.loadButton.clicked.connect(self.loadAction)
        self.spinBoxDifference.valueChanged.connect(self.spinBoxAction)

        ######################################################
        
        ##############################################################

        self.edges = np.zeros((240, 320), np.int8)
        self.imgRegions = np.full((240, 320), -1, dtype=np.int32)
        self.listRegions = []

        ##############################################################

    def spinBoxAction(self):
        if self.colorState is True:
            self.fillImgRegions()
        else: 
            self.fillImgRegionsColor()

    '''
    What we have to do is fill each region with a value.
    Iterate over the whole image. If we find a point that doesn't have a region we call floodfill
    Floodfill will fill the region using the mask with a value and give us a rectangle. Using those,
    We iterate over that rectangle and add the points with that value to imgRegions, 
    so we don't iterate multiple times over the same region. After we have done that, we regenerate the mask
    to avoid having different regions with the same value.  
    '''

    def fillImgRegions(self):

        #print("principio" + str(self.imgRegions))

        #np.set_printoptions(threshold = np.inf)

        regionID = 1
        regionList = []
        #print("imagen: " + str(self.grayImage.shape))
        # self.printNumpyArray(self.grayImage)
        self.edges = cv2.Canny(self.grayImage, 40, 120)

        # print("---")
        #print("bordes: " + str(self.edges))
        # print("Stop1")
        # self.printNumpyArray(self.edges)
        self.mask = cv2.copyMakeBorder(
            self.edges, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=255)
        # print(self.mask.shape)
        # print("Stop")
        # self.printNumpyArray(self.mask)
        #print("borders shape: " + str(self.mask.shape))
        # print("---")
        # print(self.mask)
        '''
        print("Edge size:" + str(self.edges.shape))
        print("Image shape" + str(self.grayImage.shape))
        print("Regions shape" + str(self.imgRegions.shape))
        print("We got here")
        #plt.subplot(121),plt.imshow(self.edges,cmap = 'gray')
        #plt.show()
        '''
        dialogValue = self.spinBoxDifference.value()
        print(dialogValue)
        if self.checkBoxRange.isChecked() == True:
            floodFlags = cv2.FLOODFILL_MASK_ONLY | 4 | 1 << 8
        else:
            floodFlags = cv2.FLOODFILL_MASK_ONLY | 4 | cv2.FLOODFILL_FIXED_RANGE | 1 << 8

        for i in range(0, 240, 1):
            for j in range(0, 320, 1):
                # We found a new region:

                # Optimize this, it's the part that makes it stupid slow
                if self.imgRegions[i][j] == -1:
                    if self.edges[i][j] == 0:

                        _, _, newMask, rect = cv2.floodFill(self.grayImage, self.mask, (j, i), 1, loDiff=dialogValue,
                                                            upDiff=dialogValue, flags=floodFlags)
                        print(rect)
                        newRegion = region(regionID, rect)

                        for k in range(rect[0], rect[0] + rect[2], 1):
                            for l in range(rect[1], rect[1] + rect[3], 1):
                                if newMask[l+1][k+1] == 1 and self.imgRegions[l][k] == -1:
                                    self.imgRegions[l][k] = regionID
                                    newRegion.addPoint(self.grayImage[l][k])
                        newRegion.calcAverage()
                        regionList.append(copy.deepcopy(newRegion))

                        regionID += 1
                    #self.mask = cv2.copyMakeBorder(self.edges, 1,1,1,1, cv2.BORDER_CONSTANT, value = 255)

        for i in range(1,239,1):
            for j in range(1,319,1):
                if self.imgRegions[i][j] == -1:
                    for k in range(-1,2,1):
                        for l in range(-1,2,1):
                            if self.imgRegions[i+k][j+l] != -1 and self.imgRegions[i][j] == -1:
                                self.imgRegions[i][j] = self.imgRegions[i+k][j+l]
        
        if self.checkBoxMerge.isChecked() is True:
            print("Merging")
            for i in range (1, 239, 1):
                for j in range(1, 319, 1):
                    found = False
                    for k in range(-1,2,1):
                        if found is True:
                            break
                        for l in range(-1,2,1) :
                            if found is True:
                                break
                            if self.imgRegions[i][j] != self.imgRegions[i+k][j+l]:
                                regionList[self.imgRegions[i][j]-1].addFrontierPoint([i,j, self.imgRegions[i+k][j+l]])
                                #print("Point coords: ", i, " ", j, " Region ID: ", self.imgRegions[i][j])
            for i in regionList:
                if i.deleted == False:
                    borderRegions = i.regionsInBorder()
                    for j in borderRegions:
                        otherRegion = regionList[j-1]
                        if i.regionSize() < otherRegion.regionSize():
                            smallestRegion = i.id
                            biggest = j
                        else:
                            smallestRegion = j
                            biggest = i.id
                        percentageOfBorder = regionList[smallestRegion-1].percentageOfBorder(self.edges, biggest)
                        percentageOfFrontier = regionList[smallestRegion-1].percentageOfFrontier(biggest)
                        if percentageOfBorder > 0.4 and percentageOfFrontier > 0.4:
                            for k in range(240):
                                for l in range(320):
                                    if self.imgRegions[k][l] == smallestRegion:
                                        self.imgRegions[k][l] = biggest
                            regionList[biggest-1].mergeRegion(regionList[smallestRegion-1])
                            regionList[smallestRegion-1].deleted = True
                        #regionList.pop(smallestRegion-1)

        ''' 
            Lo que tengo que hacer:
            Para cada región, mirar su frontera. Para cada valor distinto que haya, mirar cual de las dos es más pequeña.
            Para la más pequeña, mirar si el número de puntos de ese valor es mayor de un porcentaje y si no muchos de esos puntos
            pertenecen a un borde de canny. Si es así, recorrer el rectángulo de esa región y poner todos los puntos al otro valor.
        '''



        for i in range(240):
            for j in range(320):    
                regionIndex = self.imgRegions[i][j] -1
                region2 = regionList[regionIndex]
                avgGrey = region2.returnAverage()
                self.grayImageDest[i][j] = int(avgGrey)

        print("Number of regions after: ", len(regionList))

        checkBreak = False
        if self.checkBoxBorders.isChecked() == True:
            #We skip the first to avoid out of bounds. Can be done manually, or adding an if check that makes everything slow as fuck.
            for i in range(1, 239, 1):
                for j in range(1, 319, 1):
                    checkBreak = False
                    for k in range(1, -2, -1):
                        if checkBreak == True:
                            break
                        for l in range(1, -2, -1):
                            if self.imgRegions[i][j] != self.imgRegions[i+k][j+l]:
                                self.grayImageDest[i][j] = 255
                                checkBreak = True
                                break

        

        '''
        #Set borders to black.
        for i in range(0, 240, 1):
            for j in range(0, 320, 1):
                if self.imgRegions[i][j] == -1:
                    self.imgRegions[i][j] = 0       
        '''
        #print("Resultado: " + str(self.imgRegions))
        # print(self.imgRegions.shape)
        # print(np.unique(self.imgRegions))

        #plt.subplot(121),plt.imshow(self.imgRegions,cmap = 'gray')
        # plt.show()

        #cv2.imwrite("result.png", self.imgRegions)
        #self.grayImageDest = cv2.resize(self.grayImageDest, (320, 240))
        #self.grayImageDest = cv2.cvtColor(self.grayImageDest, cv2.COLOR_BGR2GRAY)
        self.visorD.set_open_cv_image(self.grayImageDest)
        self.visorD.update()
        self.imgRegions = np.full((240, 320), -1, dtype=np.int32)

    def fillImgRegionsColor(self):

        regionID = 1
        self.edges = cv2.Canny(self.colorImage, 40, 120)
        self.mask = cv2.copyMakeBorder(
            self.edges, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=255)
        '''
        #plt.subplot(121),plt.imshow(self.edges,cmap = 'gray')
        #plt.show()
        '''
        regionList = []
        dialogValue = self.spinBoxDifference.value()
        if self.checkBoxRange.isChecked() == True:
            floodFlags = cv2.FLOODFILL_MASK_ONLY | 4 | 1 << 8
        else:
            floodFlags = cv2.FLOODFILL_MASK_ONLY | 4 | cv2.FLOODFILL_FIXED_RANGE | 1 << 8

        for i in range(0, 240, 1):
            for j in range(0, 320, 1):
                # We found a new region:

                # Optimize this, it's the part that makes it stupid slow
                if self.imgRegions[i][j] == -1:
                    if self.edges[i][j] == 0:
                    

                        dialogValueArray = [dialogValue, dialogValue, dialogValue]

                        _, _, newMask, rect = cv2.floodFill(self.colorImage, self.mask, (j,i), 1, loDiff = dialogValueArray, 
                        upDiff = dialogValueArray, flags = floodFlags)
                    
                        newRegion = regionColor(regionID, rect)

                        for k in range(rect[0], rect[0] + rect[2], 1):
                            for l in range(rect[1], rect[1] + rect[3], 1):
                                if newMask[l+1][k+1] == 1 and self.imgRegions[l][k] == -1:
                                    self.imgRegions[l][k] = regionID
                                    newRegion.addPoint(self.colorImage[l][k])
                                    
                        
                    
                    #This should set the piece of grayImageDest to the correct value. Maybe move outside to increase efficiency.
                    #Use imgRegions and the regionID to set each point to the correct value, that way it's only one big loop instead
                    #of many smaller overlapping ones
                        newRegion.calcAverage()
                        regionList.append(copy.deepcopy(newRegion))
                    #print(regionID)
                        regionID += 1
                    #self.mask = cv2.copyMakeBorder(self.edges, 1,1,1,1, cv2.BORDER_CONSTANT, value = 255)
        checkBreak = False
        print("Number of regions: ", len(regionList))

        for i in range(1,239,1):
            for j in range(1,319,1):
                if self.imgRegions[i][j] == -1:
                    for k in range(-1,2,1):
                        for l in range(-1,2,1):
                            if self.imgRegions[i+k][j+l] != -1 and self.imgRegions[i][j] == -1:
                                self.imgRegions[i][j] = self.imgRegions[i+k][j+l]

        
        
        if self.checkBoxMerge.isChecked() is True:
            print("Merging")
            for i in range (1, 239, 1):
                for j in range(1, 319, 1):
                    found = False
                    for k in range(-1,2,1):
                        if found is True:
                            break
                        for l in range(-1,2,1) :
                            if found is True:
                                break
                            if self.imgRegions[i][j] != self.imgRegions[i+k][j+l]:
                                regionList[self.imgRegions[i][j]-1].addFrontierPoint([i,j, self.imgRegions[i+k][j+l]])
                                #print("Point coords: ", i, " ", j, " Region ID: ", self.imgRegions[i][j])
            for i in regionList:
                if i.deleted == False:
                    borderRegions = i.regionsInBorder()
                    for j in borderRegions:
                        otherRegion = regionList[j-1]
                        if i.regionSize() < otherRegion.regionSize():
                            smallestRegion = i.id
                            biggest = j
                        else:
                            smallestRegion = j
                            biggest = i.id
                        percentageOfBorder = regionList[smallestRegion-1].percentageOfBorder(self.edges, biggest)
                        percentageOfFrontier = regionList[smallestRegion-1].percentageOfFrontier(biggest)
                        if percentageOfBorder > 0.4 and percentageOfFrontier > 0.4:
                            for k in range(240):
                                for l in range(320):
                                    if self.imgRegions[k][l] == smallestRegion:
                                        self.imgRegions[k][l] = biggest
                            regionList[biggest-1].mergeRegion(regionList[smallestRegion-1])
                            regionList[smallestRegion-1].deleted = True

        for i in range(240):
            for j in range(320):
                regionIndex = self.imgRegions[i][j] -1
                region2 = regionList[regionIndex]
                avgColor = region2.returnAverage()
                self.colorImageDest[i][j] = avgColor

        if self.checkBoxBorders.isChecked() == True:
            #We skip the first to avoid out of bounds. Can be done manually, or adding an if check that makes everything slow as fuck.
            for i in range(1, 240, 1):
                for j in range(1, 320, 1):
                    checkBreak = False
                    for k in range(1, -2, -1):
                        if checkBreak == True:
                            break
                        for l in range(1, -2, -1):
                            if self.imgRegions[i][j] != self.imgRegions[i+k][j+l]:
                                self.colorImageDest[i][j] = [255, 255, 255]
                                checkBreak = True
                                break

        # TODO: When it finds a new region, add it to a list as a region object, with the rectangle for efficiency. When it iterates over the region to set the imgRegions,
        # it adds the value of the respective point in grayImage (or colorImage, whatever) to the region object. When it finishes adding the region, it returns the average value.
        # After we're done, we iterate through the list of regions, using the rectangle to be more efficient, and we set each pixel in grayImageDest that is inside that region
        # to the average value of the region. It should give us a nice image. The only thing left to do is to do *something* with the borders.

        '''
        #Set borders to black.
        for i in range(0, 240, 1):
            for j in range(0, 320, 1):
                if self.imgRegions[i][j] == -1:
                    self.imgRegions[i][j] = 0       
        '''
        #print("Resultado: " + str(self.imgRegions))
        # print(self.imgRegions.shape)
        # print(np.unique(self.imgRegions))

        #plt.subplot(121),plt.imshow(self.imgRegions,cmap = 'gray')
        # plt.show()

        #cv2.imwrite("result.png", self.imgRegions)
        #self.grayImageDest = cv2.resize(self.grayImageDest, (320, 240))
        #self.grayImageDest = cv2.cvtColor(self.grayImageDest, cv2.COLOR_BGR2GRAY)
        self.visorD.set_open_cv_imageColor(self.colorImageDest)
        self.visorD.update()
        self.imgRegions = np.full((240, 320), -1, dtype=np.int32)

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
            if self.colorState == True:
                self.grayImage = np.zeros((240,320), np.uint8)
                self.grayImageDest = np.zeros((240,320), np.uint8)
                self.grayImage = cv2.imread(imgPath)
                self.grayImage = cv2.resize(self.grayImage, (320, 240))
                self.grayImage = cv2.cvtColor(
                    self.grayImage, cv2.COLOR_BGR2GRAY)
                self.fillImgRegions()
                self.visorS.set_open_cv_image(self.grayImage)

            else:
                self.colorImage = np.zeros((240,320,3), np.uint8)
                self.colorImageDest = np.zeros((240,320,3), np.uint8)
                self.colorImage = cv2.imread(imgPath)
                self.colorImage = cv2.resize(self.colorImage, (320, 240))
                self.colorImage = cv2.cvtColor(
                    self.colorImage, cv2.COLOR_BGR2RGB)
                self.fillImgRegionsColor()
                self.visorS.set_open_cv_imageColor(self.colorImage)
        self.visorS.update()
        # self.test()

    def captureButtonAction(self):
        if self.captureState == False:
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
            if self.colorState == True:
                ret, self.grayImage = self.capture.read()
                if ret == False:
                    self.capture.release()
                    self.captureState = False
                    self.grayImage = np.zeros((240, 320), np.uint8)
                    self.grayImageDest = np.zeros((240, 320), np.uint8)
                    self.timer.stop()
                    self.timer.start(16)
                    return
                self.grayImage = cv2.resize(self.grayImage, (320, 240))
                self.grayImage = cv2.cvtColor(
                    self.grayImage, cv2.COLOR_BGR2GRAY)
                self.fillImgRegions()
                self.visorS.set_open_cv_image(self.grayImage)
            else:
                print("Should be here")
                ret, self.colorImage = self.capture.read()
                if ret == False:
                    self.capture.release()
                    self.captureState = False
                    self.colorImage = np.zeros((240, 320, 3))
                    self.colorImageDest = np.zeros((240, 320, 3))
                    self.timer.stop()
                    self.timer.start(16)
                    return
                self.colorImage = cv2.resize(self.colorImage, (320, 240))
                self.colorImage = cv2.cvtColor(
                    self.colorImage, cv2.COLOR_BGR2RGB)
                self.fillImgRegionsColor()
                self.visorS.set_open_cv_imageColor(self.colorImage)

        # FIXED: astype is needed to convert the cv type to the qt expected one

        # FIXED: astype is needed to convert the cv type to the qt expected one
        self.visorS.update()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())
