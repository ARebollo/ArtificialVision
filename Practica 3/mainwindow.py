from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QLabel, QGraphicsScene
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtCore import QRect, QTimer, Qt, QLineF, QPointF
import cv2
from cv2 import VideoCapture
import numpy as np
#from ImgViewer import ImgViewer
import copy
from ImageObject import ImageObject
from ImgViewer import ImgViewer

class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui_MainWindow, self).__init__()

        ##################      UI loading      ##################

        uic.loadUi('/Users/dakolas/Documents/GitHub/ArtificialVision/Practica 3/mainwindow.ui', self)
        #uic.loadUi('mainwindow.ui', self)

        self.addObject =  QtWidgets.QDialog()
        uic.loadUi('/Users/dakolas/Documents/GitHub/ArtificialVision/Practica 3/objectName.ui', self.addObject)
        #uic.loadUi('objectName.ui', self.addObject)
        self.addObject.okButton.clicked.connect(self.addOkAction)

        self.renameObject =  QtWidgets.QDialog()
        uic.loadUi('/Users/dakolas/Documents/GitHub/ArtificialVision/Practica 3/objectRename.ui', self.renameObject)
        #uic.loadUi('objectRename.ui', self.renameObject)
        self.renameObject.okButton.clicked.connect(self.renameOkAction)

        ##########################################################

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

        self.colorImageM = np.zeros((240, 700, 3))
        self.imgM = QImage(700, 240, QImage.Format_RGB888)
        self.visorM = ImgViewer(700, 240, self.imgM, self.imageFrameS_2)
        #self.visorS.set_open_cv_image(self.grayImageDest)
        
        ##############################################################################


        ##################      Buttons     ##################

        self.captureButton.clicked.connect(self.captureButtonAction)
        self.addButton.clicked.connect(self.addAction)
        self.renameButton.clicked.connect(self.renameAction)
        self.removeButton.clicked.connect(self.removeAction)
        self.loadButton.clicked.connect(self.loadAction)

        ######################################################

        
        ##################      Image matching      ##################

        #Actual imageObject objects that represent the images. Their keypoints and descriptors can also be obtained from these directly
        self.imageList = []
        #A dictionary mapping object names in the comboBox to the actual objects
        self.mapObjects = {}
        #In these, 0:2 are the first object, 3:5 the second and 6:8 the third. The last are the keypoints of the actual image.
        #They are all a list of lists.
        self.ObjectKeyPointList = []
        #Keypoints of the captured image. 
        self.imageKeypointList = []
        #ORB and BFMatcher, using Hamming distance.
        self.orb = cv2.ORB_create()
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        
        ##############################################################
        
        #self.retranslateUi(MainWindow)
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

        ##################      Signals     ##################

        self.visorS.windowSelected.connect(self.selectWindow)
        self.visorS.pressEvent.connect(self.deSelectWindow)

        ######################################################

        '''
            To use: findHomography(), with LMEDS.
            Para hacer la transformación de vectores, se usa perspectiveTransform()
            Se parte de las listas de keypoints: la de la imagen y la del objeto
            con la escala seleccionada. QueryIdx son los de la imagen, trainIdx los del objeto.
            Tras selecciona el knnmatch con mas 
        
        
        '''

    def loadAction(self):
        if len(self.objectList) != 3:
            imgPath, _ = QFileDialog.getOpenFileName()
            if imgPath != "":
                self.grayImageLoad = cv2.imread(imgPath)
                self.grayImageLoad = cv2.resize(self.grayImageLoad, (240,180))
                self.grayImageLoad = cv2.cvtColor(self.grayImageLoad, cv2.COLOR_BGR2GRAY)

                imgName = imgPath
                image = ImageObject(imgName, self.grayImageLoad, self.orb)
                kp, desc, valid = image.returnKpDes()
                if valid is True:
                    self.imageList.append(image)
                    self.mapObjects[imgName] = self.imageList[-1]
                    self.objectList.addItem(imgName)
                    #Get the image descriptors and add them to the descriptor collection

                    print("DESC:")
                    for i in desc:
                        print(len(i))
                        self.bf.add([i])
                    print("KP:")
                    for i in kp:
                        print(len(i))
                        self.ObjectKeyPointList.append([i])     
                else:
                    message = QtWidgets.QMessageBox()
                    message.about(None, 'Error', 'Error adding object: The selected object is not descriptive enough.')




        else:
            message = QtWidgets.QMessageBox()
            message.about(None, 'Error', 'Error loading image: Maximum number of objects reached.')

    #Calculates the matches between the image captured by the webcam/video and the objects stored. Stores them in obtainedMatches().
    #Returns a list containing, for each of the three (or two, or however many there are), the scale with the most matches.
    def calculateMatches(self):
        if len(self.bf.getTrainDescriptors())!= 0:
            self.imageKeypointList, des = self.orb.detectAndCompute(self.grayImage, None)
            #print(len(des))
            obtainedMatches = self.bf.knnMatch(des, k = 3)
            goodMatches = []
            for i in range(len(self.imageList*3)):
                goodMatches.append([])
            #Iterate over the collection of matches
            for i in obtainedMatches:
                #Iterate over each triplet of best matches for each descriptor
                for j in i:
                    #Tells us that the match is valid, and inserts it in the appropiate list
                    if j.distance < 50:
                        goodMatches[j.imgIdx].append(j)
                        

            #Create a list of <number of images> elements. For each object, we find the scale with the most matches, and add all the matches in its list
            #to the list of lists bestScaleList.
            bestScaleList = []
            for i in range(0, len(self.imageList), 1):
                print("i: " + str(i))
                print("len imagelist: " + str(len(self.imageList)))
                bestScaleList.append([])
            #Iterate over the goodmatches list, for each element get the scale with the most matches
            for i in range(0,len(goodMatches),3):
                bestScale = []
                matchCount = 0
                for j in range(3):
                    if len(goodMatches[j]) > matchCount:
                        bestScale = goodMatches[j]
                        matchCount = len(goodMatches[j])
                    bestScaleList.append(bestScale)
            
            print("bestScaleList len: " + str(len(bestScaleList)))

            #After this, bestScaleList should have <number of items> elements, and each element is a list containing the matches each object, for the scale with the most matches            
            
        #INFO and TODO: obtainedMatches is a list of lists that contains, for each keypoint in the image, a list of the k best matches as a DMatch object
        #What we have to do is iterate over that list, choosing the valid matches and adding them to a list of valid matches. That list has 3*object elements
        #and each element contains the matches for that object and scale. After that is done, for each object we choose the scale with the most matches and 
        #choose it as the best one. 
        #Then, we have to get the pair <keypoint, matchedKeypoint> (the image ones are stored in self.imageKeypointList, index queryIdx,
        #the object ones are stored in self.objectKeypointList, index trainIdx. After matching them, choose if a set of matches for an object actually represents and object
        #(minimum number of matches) and apply the homography. Draw it.
            
            self.ObjectKeyPointList, des2 = self.orb.detectAndCompute(self.imageWindow, None)

            # Match features.
            matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
            matches = matcher.match(des, des2, None)
            
            # Sort matches by score
            matches.sort(key=lambda x: x.distance, reverse=False)
            
            # Remove not so good matches
            numGoodMatches = int(len(matches) * 0.15)
            matches = matches[:numGoodMatches]

            # Extract location of good matches
            points1 = np.zeros((len(matches), 2), dtype=np.float32)
            points2 = np.zeros((len(matches), 2), dtype=np.float32)

            for i, match in enumerate(matches):
                points1[i, :] = self.imageKeypointList[match.queryIdx].pt
                points2[i, :] = self.ObjectKeyPointList[match.trainIdx].pt
        
            # Find homography
            h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

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
        self.addObject.hide()

        if self.actionReady is True:
            #Get coordinates and size of the selected rectangle
            y_OffSet = self.imageWindow.y()
            x_OffSet = self.imageWindow.x()
            height = self.imageWindow.height()
            width = self.imageWindow.width()
            
            #Get the relevant slice of the source image
            crop_img = copy.copy(self.grayImage[y_OffSet:y_OffSet + height, x_OffSet:x_OffSet + width])
            
            
            #Add the image to the comboBox and the list
            imgName = self.addObject.lineEdit.text()
            image = ImageObject(imgName, crop_img, self.orb)
            kp, desc, valid = image.returnKpDes()
            if valid is True:
                self.imageList.append(image)
                self.mapObjects[imgName] = self.imageList[-1]
                self.objectList.addItem(imgName)
                #Get the image descriptors and add them to the descriptor collection
            
            
                print("DESC:")
                for i in desc:
                    print(len(i))
                    self.bf.add([i])
                print("KP:")
                for i in kp:
                    print(len(i))
                    self.ObjectKeyPointList.append([i])     
            else:
                message = QtWidgets.QMessageBox()
                message.about(None, 'Error', 'Error adding object: The selected object is not descriptive enough.')
    def renameAction(self):
        self.renameObject.show()

    def renameOkAction(self):
        self.renameObject.hide()

    def removeAction(self):
        del self.imageList[self.objectList.currentIndex()]
        self.objectList.removeItem(self.objectList.currentIndex())
        for i in range(self.objectList.currentIndex(),self.objectList.currentIndex()+2,1):
            del self.imageKeypointList[i]
        #TODO: Regenerar bien listas de descriptores y keypoints
        self.bf.clear()
        for i in self.imageList:
            _, des = i.returnKpDes()
            self.bf.add([des])

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
            self.calculateMatches()
            #print(matches)
            #print(keypoints)
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
