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

        self.colorImageM = np.zeros((240, 700, 3))
        self.colorImageM = cv2.imread("Practica 3/noMatches.jpg")
        self.imgM = QImage(700, 240, QImage.Format_RGB888)
        self.visorM = ImgViewer(700, 240, self.imgM, self.imageFrameS_2)
        #self.visorS.set_open_cv_image(self.grayImageDest)
        
        ##############################################################################


        ##################      Buttons     ##################

        self.captureButton.clicked.connect(self.captureButtonAction)
        self.addButton.clicked.connect(self.addAction)
        self.loadButton.clicked.connect(self.loadAction)
        self.loadButton_Video.clicked.connect(self.loadVideoAction)

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

    def loadVideoAction(self):
        imgPath, _ = QFileDialog.getOpenFileName()
        if imgPath != "":
            self.captureState = True
            self.capture = VideoCapture(imgPath)
            self.timer.stop()
            fps = self.capture.get(cv2.CAP_PROP_FPS)
            self.timer.start(1000/fps)

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
