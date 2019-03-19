import cv2
import numpy as np
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QRect, QTimer, Qt, QPointF
from PyQt5.QtGui import QImage
from cv2 import VideoCapture

# from ImgViewer import ImgViewer
from ImgViewer import ImgViewer


class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        print("Trying to connect")


        self.capture = VideoCapture(0)
        self.captureState = True
        self.captureButtonAction()
        self.winSelected = False

        # Timer to control the capture.
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerLoop)
        self.timer.start(16)

        # FIXED: Opencv images where created with wrong width height values (switched) so the copy failed
        # self.colorImage = np.zeros((320,240))
        # FIXED: original removed 2 of the 3 chanels with the np.zeros
        # self.colorImage = np.zeros((320,240))
        # self.colorImage = np.zeros((240,320,3))
        self.grayImage = np.zeros((240, 320), np.uint8)
        # self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)
        self.imgS = QImage(320, 240, QImage.Format_Grayscale8)
        self.visorS = ImgViewer(320, 240, self.imgS, self.imageFrameS)
        self.imageWindow = QRect()



        # FIXED: original removed 2 of the 3 chanels with the np.zeros
        # self.colorImageDest = np.zeros((240,320))
        # self.colorImageDest = np.zeros((240,320,3))
        self.grayImageDest = np.zeros((240, 320), np.uint8)
        # self.grayImage = cv2.cvtColor(self.grayImageDest, cv2.COLOR_BGR2GRAY)
        self.imgD = QImage(320, 240, QImage.Format_Grayscale8)
        self.visorD = ImgViewer(320, 240, self.imgD, self.imageFrameD)


        self.captureButton.clicked.connect(self.captureButtonAction)
        self.visorS.windowSelected.connect(self.selectWindow)
        self.visorS.pressEvent.connect(self.deselectWindow)

        # self.loadButton.clicked.connect(self.loadImageAction)




    def captureButtonAction(self):
        if self.captureState == False:
            self.captureButton.setText("Stop Capture")
            self.captureButton.setChecked(True)
            print("Started")
            self.captureState = True
        else:
            self.captureButton.setText("Start Capture")
            self.captureButton.setChecked(False)
            print("Stopped")
            self.captureState = False

    def timerLoop(self):
        if (self.captureState == True and self.capture.isOpened() == True):
            ret, self.grayImage = self.capture.read()
            self.grayImage = cv2.resize(self.grayImage, (320, 240))
            self.grayImage = cv2.cvtColor(self.grayImage, cv2.COLOR_BGR2GRAY)


        # FIXED: astype is needed to convert the cv type to the qt expected one


        if self.winSelected:
            self.visorS.drawSquare(self.imageWindow, Qt.green)
        self.visorS.set_open_cv_image(self.grayImage)
        # FIXED: astype is needed to convert the cv type to the qt expected one
        self.visorD.set_open_cv_image(self.grayImageDest)
        self.visorS.update()
        self.visorD.update()

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

    def deselectWindow(self):
        self.winSelected = False


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())