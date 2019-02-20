#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 12:10:15 2019

@author: dakolas
"""

import collections as c
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

class ImgViewer: 

#Q_OBJECT
    
    TRect = c.namedtuple('TRect', 'rect color id ang fill width')
    TEllipse = c.namedtuple('TEllipse', 'rect center rx ry color id fill ang')
    TLine = c.namedTuple('TLine', 'line color width')
    TGrad = c.namedTuple('TGrad', 'line color color1 width')
    TText = c.namedTuple('TText', 'pos size color text width')

    imageScale = 0.0
    invertedVerticalAxis = False
    
    width = 0
    height = 0
    win = QtCore.QRectF()
    effWin = QtCore.QRectF()
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
    pressEvent = QtCore.pyqtSignal(int)

    #imgVisor input qimage, imgFrame qimage parent
    def __init__(self, width, heigth, imgVisor, imgFrame):
        
        QtWidgets.resize(width,heigth)
        QtCore.win.setRect(0,0,width,heigth)

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
            self.ctable.append([i,i,i])
    
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
        QtWidgets.show()

         
    def mousePressEvent(self, mouseEvent):
        if mouseEvent.button() == QtCore.LeftButton:
            self.iniCoorSelected.setX(mouseEvent.x())
            self.iniCoorSelected.setY(mouseEvent.y())
            self.endCoorSelected.setX(mouseEvent.x())
            self.endCoorSelected.setY(mouseEvent.y())

            self.onSelection = True
            self.pressEvent.emit()

    def mouseMoveEvent(self, mouseEvent):
        self.endCoorSelected.setX(mouseEvent.x())
        self.endCoorSelected.setY(mouseEvent.y())
    
    def mouseReleaseEvent(self, mouseEvent):
        if mouseEvent.button() == QtCore.LeftButton:
            self.windowSelected((self.iniCoorSelected+self.endCoorSelected)/2, abs(self.endCoorSelected.x()-self.iniCoorSelected.x()),
            abs(self.endCoorSelected.y()-self.iniCoorSelected.y())).emit()
        self.onSelection = False
    

'''
void setImage(QImage *img);
void paintEvent(QPaintEvent *);
void setWindow(const QRect & win_) { effWin = win = win_; }
void drawSquare(const QRect &, const QColor &,  bool fill=false, int id= -1, float rads=0, float width=0);
void drawSquare(const QPoint &, int sideX, int sideY, const QColor &,  bool fill=false , int id= -1, float rads=0, float width=0);
void drawSquare(const QPointF &, int sideX, int sideY, const QColor &,  bool fill=false , int id= -1, float rads=0, float width=0);
void drawLine(const QLine &line, const QColor & c, float width=0);
void drawLine(const QLineF &line, const QColor & c, float width=0);
void drawLineOnTop(const QLine &line, const QColor & c, float width=0);
void drawLineOnTop(const QLineF &line, const QColor & c, float width=0);
void drawLineFOnTop(const QLineF &line, const QColor & c, float width=0);
void drawPolyLine(const QVector<QPoint> & pline, const QColor & c, int width=1);
void drawPolyLine(const QVector<int> & xs, const QVector<int> & ys, const QColor & c, int width=1);
void drawGrad(const QLine &line, const QColor & c, const QColor & c1, float width=0);
void drawEllipse(const QRect &, const QColor &, bool fill= false, int id =-1, float rads=0);
void drawEllipse(const QPointF &, int radiusX, int radiusY, const QColor &, bool fill=false, int id =-1, float rads=0);
void drawEllipse(const QPoint &, int radiusX, int radiusY, const QColor &, bool fill=false, int id =-1, float rads=0);
void drawAxis(const QColor &, int w);
void drawPerimeter(const QColor &c, int width, int margin);
void drawPerimeter(const QColor &c, int width);
void drawCrossHair(const QColor &c);
void drawText(const QPoint & pos, const QString & text, int size, const QColor & color);
void scaleImage(float sscale) { imageScale = sscale; setFixedSize(sscale*width, sscale*height); }
    
void setDrawAxis(bool f) { DRAW_AXIS = f;}
void setDrawPerimeter(bool f) { DRAW_PERIMETER = f;}
QRectF getWindow() { return win;}
    
uint32_t getWidth() { return width; }
uint32_t getHeight() { return height; }
void autoResize();
uchar *imageBuffer() { if (qimg != NULL) return qimg->bits(); return NULL; }
'''