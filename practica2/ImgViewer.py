#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 12:10:15 2019

@author: dakolas
"""

import collections as c
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPainter
#from PyQt5.QtGui import QMouseEvent
from PyQt5.QtOpenGL import QGLWidget
class ImgViewer(QGLWidget): 

#Q_OBJECT
    
    TRect = c.namedtuple('TRect', 'rect color id ang fill width')
    #TEllipse = c.namedtuple('TEllipse', 'rect center rx ry color id fill ang')
    #TLine = c.namedTuple('TLine', 'line color width')
    #TGrad = c.namedTuple('TGrad', 'line color color1 width')
    #TText = c.namedTuple('TText', 'pos size color text width')

    imageScale = 0.0
    invertedVerticalAxis = False
    
    width = 0
    height = 0
    win = QtCore.QRect()
    effWin = QtCore.QRect()
    #Queue<TRect>
    squareQueue = c.deque()
    #Queue<TLine>
    lineQueue = c.deque()
    #Queue<TEllipse>
    lineOnTopQueue = c.deque()
    #Queue<TGrad>
    gradQueue = c.deque()
    #Queue<TText>
    textQueue = c.deque()

    qimg = QtGui.QImage()
    #For gray conversion -> Array<QRgb>
    ctable = list()
    inicio = QtCore.QPoint()
    actual = QtCore.QPoint()
    translating = False
    backPos = QtCore.QPointF()
    DRAW_AXIS = False
    DRAW_PERIMETER = False

    linGrad = QtGui.QLinearGradient()
    
    iniCoorSelected = QtCore.QPointF()
    endCoorSelected = QtCore.QPointF()
    onSelection = False  
 
    #signals:
    windowSelected = QtCore.pyqtSignal(QtCore.QPointF, int, int)
    pressEvent = QtCore.pyqtSignal()

    #imgVisor input qimage, imgFrame qimage parent
    def __init__(self, width, heigth, imgVisor, imgFrame):
        
        super(  ).__init__(imgFrame)
        
        self.resize(width,heigth)
        self.win.setRect(0,0,width,heigth)
        self.setGeometry(self.win)
        if imgVisor is not None:
            self.qimg = imgVisor
        
        self.invertedVerticalAxis = False
        self.W_AXIS = False
        self.W_PERIMETER = False
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