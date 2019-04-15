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
        self.colorImageM = cv2.imread("Practica 3/noMatches.jpg")
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
                #print("escala: " + str(self.grayImageLoad.shape))
                y, x, a = self.grayImageLoad.shape
                scaleFactor = x/y
                #print("scaleFactor: " + str(scaleFactor))
                width = int(180*scaleFactor)
                height = int(180)
                dim = (width, height)
                self.grayImageLoad = cv2.resize(self.grayImageLoad, dim)
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
            obtainedMatches = self.bf.knnMatch(des, k = 3)
            
            #print("obtainedMatches" + str([len(z) for z in obtainedMatches]))
            
            orderedMatches = [[] for z in range(len(self.imageList)*3)]
            for l in obtainedMatches:
                for m in l:
                    #print("match id: " + str(m.imgIdx))
                    if (m.imgIdx < len(self.imageList)*3): #Ñapa, pero es que daba ID =  1056 y eso no tiene ni puto sentido
                        orderedMatches[m.imgIdx].append(m)
            
            #print("before" + str(len(orderedMatches[1])))
            #print("obtainedMatches length" + str(len(obtainedMatches)))
     
            #print("keypoints antes 1: " + str(len(self.imageList[0].returnKpDes()[0][0])))
            #print("keypoints antes 2: " + str(len(self.imageList[0].returnKpDes()[0][1])))
            #print("keypoints antes 3: " + str(len(self.imageList[0].returnKpDes()[0][2])))
            GoodOrderedMatches = []
            #Iterate over the collection of matches

            '''
            for i in orderedMatches:
                newOrderedMatches = []
                for id in range (len(i)):
                    #Tells us that the match is valid, and inserts it in the appropiate list
                    if id < len(i) - 1:
                        #print("id: " + str(id) + "len i: " + str(len(i)))
                        if i[id].distance < i[id + 1].distance * 0.8:
                            newOrderedMatches.append(i[id])
                    GoodOrderedMatches.append(newOrderedMatches)
            
            orderedMatches = GoodOrderedMatches
            '''

            #print("antes " + str(len(orderedMatches[0])))

            '''
            aux = copy.copy(orderedMatches)

            for i in aux:
                for j in i:
                    if j.distance > 0:
                        i.remove(j)
                        
            orderedMatches = copy.copy(aux)
            '''

            for i in orderedMatches:
                j = 0
                while j < len(i):
                    if i[j].distance > 50:
                        i.pop(j)
                    else:
                        j += 1

            #print("despues" + str(len(orderedMatches[0])))

            #print("after" + str(len(orderedMatches[1])))
            #print("orderedMatches" + str([len(z) for z in orderedMatches]))
            
            #Iterate over the list of objects, and an id from 0 to number of objects
            for id, image in enumerate(self.imageList, 0):
                index = id*3
                # Sorts the orderedMatches by the number of matches of each scale, picks the one with most matches and 
                # assigns it to scaleWithMostMatches, also returns the position on x
                scaleWithMostMatches = sorted([[x,y] for x,y in enumerate(orderedMatches[index:index+3], 0)], 
                key = lambda x: len(x[1]), reverse = True)[0]

                imageScales = orderedMatches[index:index+3]
                mostMatchesId = -1
                mostMatchesNum = -1
                mostMatches = []
                for i in range(len(imageScales)):
                    #print("Matches for scale " + str(i) + ": " + str(len(imageScales[i])))
                    if len(imageScales[i]) > mostMatchesNum:
                        mostMatches = imageScales[i]
                        mostMatchesNum = len(imageScales[i])
                        mostMatchesId = i
                
                self.colorImageM = np.zeros((700, 240, 3))
                self.colorImageM = cv2.imread("Practica 3/noMatches.jpg")
                self.visorM.set_open_cv_imageColor(self.colorImageM)
                #self.noMatchesImg = cv2.resize(self.noMatchesImg, (700, 240))
                #self.visorM.set_open_cv_imageColor(self.noMatchesImg)
                self.visorM.update()

                #print(len(scaleWithMostMatches[1]))
                if (len(mostMatches) > 50):
                #if (len(scaleWithMostMatches[1]) > 10):
                    points1 = []
                    points2 = []
                    for j in mostMatches:
                    #for j in scaleWithMostMatches[1]:
                        points1.append(self.imageKeypointList[j.queryIdx].pt)
                        #print("..." + str(len(image.returnKpDes()[0][scaleWithMostMatches[0]])))
                        #print("trainidx" + str(j.trainIdx))
                        imageKp, _, _ = image.returnKpDes()
                        imageKp = imageKp[mostMatchesId]
                        #print("Should be a number: " + str(len(imageKp)) + " The one that crashes it: " + str(j.trainIdx))
                        points2.append(imageKp[j.trainIdx].pt)

                    #print("Points1: " + str(len(points1)) + " Points2: " + str(len(points2)))
                    h, mask = cv2.findHomography(np.array(points2), np.array(points1), cv2.RANSAC)

                    if h is not None:
                        if len(mostMatches) > 50:

                            corners = np.zeros((4,2), dtype=np.float32)

                            corners[1, 0] = image.getScales()[mostMatchesId].shape[1]
                            corners[2, 0] = image.getScales()[mostMatchesId].shape[1]
                            corners[2, 1] = image.getScales()[mostMatchesId].shape[0]
                            corners[3, 1] = image.getScales()[mostMatchesId].shape[0]

                            #for id, i in enumerate(corners, 0):
                            #    print("Corner " + str(id) + " : " + str(i))

                            #print("corners: " + str(corners))
                        
                            M = cv2.perspectiveTransform(np.array([corners]), h)

                            #print("M: " + str(M))

                            cv2.line(self.grayImage, (M[0][0][0], M[0][0][1]), (M[0][1][0], M[0][1][1]), (255,255,255), 4)
                            cv2.line(self.grayImage, (M[0][1][0], M[0][1][1]), (M[0][2][0], M[0][2][1]), (255,255,255), 4)
                            cv2.line(self.grayImage, (M[0][2][0], M[0][2][1]), (M[0][3][0], M[0][3][1]), (255,255,255), 4)
                            cv2.line(self.grayImage, (M[0][3][0], M[0][3][1]), (M[0][0][0], M[0][0][1]), (255,255,255), 4)
                            
                            #imageAux = np.zeros((240, 320), np.uint8)
                            imageAux = self.mapObjects[self.objectList.currentText()]
                            imageAux = np.array(imageAux.getScales()[0], dtype=np.uint8)

                            self.showMatAction(self.grayImage, self.imageKeypointList, 
                            imageAux, self.ObjectKeyPointList[mostMatchesId], orderedMatches)
                                          
    def showMatAction(self, img1, kp1, img2, kp2, matches):
        
        # BGR (142, 255, 132) light blue
        # (255, 102, 51) light green
        self.colorImageM = cv2.drawMatchesKnn(img1, kp1, img2, kp2[0], matches[0:1], None, flags=2, matchColor=(142, 255 ,132))
        #cv2.imwrite('prueba.png', self.colorImageM)
        self.colorImageM = cv2.resize(self.colorImageM, (700, 240))
        self.colorImageM = cv2.cvtColor(self.colorImageM, cv2.COLOR_BGR2RGB)
        self.visorM.set_open_cv_imageColor(self.colorImageM)
        self.visorM.update()
    
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
                auxList = []
                for i in desc:
                    print(len(i))
                    auxList.append(i)
                self.bf.add(auxList)
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
        if self.objectList.currentIndex() is not -1:
            del self.imageList[self.objectList.currentIndex()]
        self.objectList.removeItem(self.objectList.currentIndex())
        for i in range(self.objectList.currentIndex(),self.objectList.currentIndex()+2,1):
            if i is not None:
                del self.imageKeypointList[i]
        #TODO: Regenerar bien listas de descriptores y keypoints
        self.bf.clear()
        for i in self.imageList:
            _, des, _ = i.returnKpDes()
            for i in des:
                self.bf.add([i])

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
