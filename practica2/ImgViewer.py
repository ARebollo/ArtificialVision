#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 12:10:15 2019

@author: dakolas
"""

import collections as c
import signal
import sys

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPainter, QImage, QPen, QBrush
#from PyQt5.QtGui import QMouseEvent
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtWidgets import QApplication, QFrame, QWidget, QVBoxLayout

#Q_OBJECT
    
class TLine:
    line = None
    color = None
    width = None
    def __init__(self):
        pass

class ImgViewer(QWidget):
#Q_OBJECT
    # TRect = c.namedtuple('TRect', 'rect color id ang fill width')
    # #TEllipse = c.namedtuple('TEllipse', 'rect center rx ry color id fill ang')
    # #TLine = c.namedTuple('TLine', 'line color width')
    # #TGrad = c.namedTuple('TGrad', 'line color color1 width')
    # #TText = c.namedTuple('TText', 'pos size color text width')
    #
    

    #signals:
    windowSelected = QtCore.pyqtSignal(QtCore.QPointF, int, int)
    pressEvent = QtCore.pyqtSignal()

    #imgVisor input qimage, imgFrame qimage parent
    def __init__(self, width, height, q_img, imgFrame):
        super(ImgViewer, self).__init__()
        self.imageScale = 1.0
        self.invertedVerticalAxis = False
        
        # width = 0
        # height = 0
        self.win = QtCore.QRect()
        self.effWin = QtCore.QRect()
        # Queue<TRect>
        self.squareQueue = c.deque()
        # Queue<TLine>
        self.lineQueue = c.deque()
        # Queue<TEllipse>
        self.lineOnTopQueue = c.deque()
        # Queue<TGrad>
        self.gradQueue = c.deque()
        # Queue<TText>
        self.textQueue = c.deque()
        
        self.qimg = None
        # For gray conversion -> Array<QRgb>
        self.ctable = list()
        self.inicio = QtCore.QPoint()
        self.actual = QtCore.QPoint()
        self.translating = False
        self.backPos = QtCore.QPointF()
        self.DRAW_AXIS = False
        self.DRAW_PERIMETER = False
        
        self.linGrad = QtGui.QLinearGradient()

        self.iniCoorSelected = QtCore.QPointF()
        self.endCoorSelected = QtCore.QPointF()
        self.onSelection = False
        # self.layout = QVBoxLayout()
        # imgFrame.setLayout(self.layout)
        self.resize(width, height)
        self.setParent(imgFrame)
        # self.layout.addWidget(self)
        # self.layout.setContentsMargins(0,0,0,0)
        # self.resize(width,height)
        # self.win.setRect(0,0,width,height)
        # self.setGeometry(self.win)
        # self.invertedVerticalAxis = False
        # self.W_AXIS = False
        # self.W_PERIMETER = False
        self.imageScale = 1.0
    
        if self.qimg is not None:
            self.imageScale = width/self.qimg.width()
    
        else:
            self.qimg = QtCore.QImage(width,heigth, QtCore.QImage.Format_Indexed8)
            self.qimg.fill(240)
            
        for i in range (0,256):
            #ctable[i] = QtCore.qRgb(i,i,i)
            self.ctable.append(QtGui.qRgb(i,i,i))
    
        self.qimg.setColorTable(self.ctable)
        self.translating = False
        self.effWin = self.win
        
        '''
        QGLFormat f = format()
    
        if f.sampleBuffers():
            f.setSampleBuffers(true)
           setFormat(f)
            print("Sample Buffers On in QGLWidget")
    
        else:
            print("Sample Buffers Off in QGLWidget")
        '''
        
        self.onSelection = False
        self.show()
         
    def mousePressEvent(self, mouseEvent: QtGui.QMouseEvent):
        print("Mouse clicked")
        if mouseEvent.button() == QtCore.Qt.LeftButton:
            self.iniCoorSelected.setX(mouseEvent.x())
            self.iniCoorSelected.setY(mouseEvent.y())
            self.endCoorSelected.setX(mouseEvent.x())
            self.endCoorSelected.setY(mouseEvent.y())
            
            self.onSelection = True
            self.pressEvent.emit()

    def mouseMoveEvent(self, mouseEvent: QtGui.QMouseEvent):
        self.endCoorSelected.setX(mouseEvent.x())
        self.endCoorSelected.setY(mouseEvent.y())
    
    def mouseReleaseEvent(self, mouseEvent: QtGui.QMouseEvent):
        print("Mouse Released")
        if mouseEvent.button() == QtCore.Qt.LeftButton:
            self.windowSelected.emit((self.iniCoorSelected+self.endCoorSelected)/2, abs(self.endCoorSelected.x()-self.iniCoorSelected.x()),
            abs(self.endCoorSelected.y()-self.iniCoorSelected.y()))
        self.onSelection = False
    
    def drawSquare(self, posX, posY, width, height):
        painter = QPainter(self.qimg)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtCore.Qt.green)
        painter.drawRect(posX,posY,width,height)
        #ui.imageLabel->setPixmap(QPixmap::fromImage(qImage));
    def drawLine(self, line, color, width=1):
        l = TLine()
        l.line = line
        l.color = color
        l.width = width
        self.lineQueue.append(l)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.save()
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        if self.qimg is not None:
            # painter.drawImage(QRectF(0., 0., self.width(), self.height()), self.qimg)
            painter.drawImage(QRectF(0., 0., self.width(), self.height()), self.qimg,
                                      QRectF(0, 0, self.qimg.width(), self.qimg.height()))


        while len(self.lineQueue)>0:
            l = self.lineQueue.pop()
            painter.setPen(QPen(QBrush(l.color), l.width))
            painter.drawLine(l.line)
        painter.restore()
        super(ImgViewer, self).paintEvent(event)


    # def getHeight(self):
    #     return self.height
    #
    # def resizeEvent(self, event):
    #     self.repaint()
    #     super(ImgViewer, self).resizeEvent(event)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = QFrame()
    img = QImage()
    img.load("/home/robolab/PycharmProjects/ArtificialVision/practica2/kitchen-2165756_1920.jpg")
    img_viewer = ImgViewer(320,240,img, frame)
    frame.show()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.exec_()
