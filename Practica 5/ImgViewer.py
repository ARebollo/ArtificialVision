# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 12:10:15 2019

@author: dakolas
"""

import collections as c
import math
import signal
import sys
from math import fabs

import numpy as np
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRectF, QRect, QPointF, Qt
from PyQt5.QtGui import QPainter, QImage, QPen, QBrush, QColor
# from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QFrame, QWidget


class TLine:
    line = None
    color = None
    width = None

    def __init__(self):
        pass


class TRect:
    rect = QRect()
    color = QColor()
    id = 0
    ang = 0
    fill = False
    width = 0.


class ImgViewer(QWidget):
    # Q_OBJECT
    # TRect = c.namedtuple('TRect', 'rect color id ang fill width')
    # #TEllipse = c.namedtuple('TEllipse', 'rect center rx ry color id fill ang')
    # #TLine = c.namedTuple('TLine', 'line color width')
    # #TGrad = c.namedTuple('TGrad', 'line color color1 width')
    # #TText = c.namedTuple('TText', 'pos size color text width')
    #

    # signals:
    windowSelected = QtCore.pyqtSignal(QtCore.QPointF, int, int)
    pressEvent = QtCore.pyqtSignal()

    # imgVisor input qimage, imgFrame qimage parent
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

        if q_img is not None:
            self.qimg = q_img
            self.imageScale = width / self.qimg.width()
        else:
            self.qimg = QImage(width, height, QImage.Format_Grayscale8)
            self.qimg.fill(240)
            self.imageScale = width / self.qimg.width()

        #
        # for i in range (0,256):
        #     #ctable[i] = QtCore.qRgb(i,i,i)
        #     self.ctable.append(QtGui.qRgb(i,i,i))
        #
        # # self.qimg.setColorTable(self.ctable)
        # self.translating = False
        # self.effWin = self.win

        '''
        QGLFormat f = format()

        if f.sampleBuffers():
            f.setSampleBuffers(true)
           setFormat(f)
            print("Sample Buffers On in QGLWidget")

        else:
            print("Sample Buffers Off in QGLWidget")
        '''
        #
        # self.onSelection = False
        # self.show()



    def mousePressEvent(self, mouseEvent: QtGui.QMouseEvent):
        print("Mouse clicked")
        if mouseEvent.button() == QtCore.Qt.LeftButton:
            self.iniCoorSelected.setX(mouseEvent.x())
            self.iniCoorSelected.setY(mouseEvent.y())
            self.endCoorSelected.setX(mouseEvent.x())
            self.endCoorSelected.setY(mouseEvent.y())
            self.onSelection = True
            self.pressEvent.emit()
        super(ImgViewer, self).mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent: QtGui.QMouseEvent):
        self.endCoorSelected.setX(mouseEvent.x())
        self.endCoorSelected.setY(mouseEvent.y())
        super(ImgViewer, self).mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent: QtGui.QMouseEvent):
        print("Mouse Released")
        if mouseEvent.button() == QtCore.Qt.LeftButton:
            self.windowSelected.emit((self.iniCoorSelected + self.endCoorSelected) / 2,
                                     abs(self.endCoorSelected.x() - self.iniCoorSelected.x()),
                                     abs(self.endCoorSelected.y() - self.iniCoorSelected.y()))
        self.onSelection = False
        super(ImgViewer, self).mouseReleaseEvent(mouseEvent)


    def drawSquare(self, rect,  col,  fill=False , id= -1, rads=0, width=0):
        r = TRect
        r.rect = rect
        r.color = col
        r.id = id
        r.fill = fill
        r.ang = rads * 180. / math.pi
        r.width = width
        self.squareQueue.append(r)

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

        while len(self.lineQueue) > 0:
            l = self.lineQueue.pop()
            painter.setPen(QPen(QBrush(l.color), l.width))
            painter.drawLine(l.line)

        pen = painter.pen()
        # penwidth = pen.width()
        while len(self.squareQueue) > 0:
            r = self.squareQueue.pop()
            if r.fill is True:
                painter.setBrush(r.color)
            else:
                painter.setBrush(Qt.transparent)
            pen.setColor(r.color)
            pen.setWidth(r.width)
            painter.setPen(pen)
            if fabs(r.ang) > 0.01:
                center = r.rect.center()
                painter.translate(center)
                painter.rotate(r.ang)
                painter.drawRoundedRect(QRect(r.rect.topLeft() - center, r.rect.size()), 40, 40)
                painter.rotate(-r.ang)
                painter.translate(-center)
            else:
                painter.drawRect(r.rect)
            if r.id >= 0:
                painter.drawText(QPointF(r.rect.x(), r.rect.y()), s.setNum(r.id))

        painter.restore()
        super(ImgViewer, self).paintEvent(event)

    # def getHeight(self):
    #     return self.height
    #
    # def resizeEvent(self, event):
    #     self.repaint()
    #     super(ImgViewer, self).resizeEvent(event)

    def set_open_cv_image(self, opencv_img):
        for i in opencv_img:
            i = [i,i,i]
        self.qimg = QImage(opencv_img, opencv_img.shape[1], opencv_img.shape[0], opencv_img.strides[0],
                           QImage.Format_RGB88w8)
        
    def set_open_cv_imageColor(self, opencv_img):
        self.qimg = QImage(opencv_img, opencv_img.shape[1], opencv_img.shape[0], opencv_img.strides[0], QImage.Format_RGB888)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = QFrame()
    img = QImage()
    img.load("/home/robolab/PycharmProjects/ArtificialVision/practica2/kitchen-2165756_1920.jpg")
    img_viewer = ImgViewer(320, 240, img, frame)
    frame.show()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.exec_()
