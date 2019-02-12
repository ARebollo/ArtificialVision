#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 12:10:15 2019

@author: dakolas
"""

import QtGui, QGLWidget

class ImgViewer: 

#Q_OBJECT
    
    imageScale = 0.0
	invertedVerticalAxis = false
    width = 0
    height = 0
	win = QRectF()
	effWin = QRectF()
	squareQueue = QQueue<TRect>()
	lineQueue = QQueue<TLine> ()
	lineOnTopQueue = QQueue<TLine>()
	ellipseQueue = QQueue<TEllipse>()
	gradQueue = QQueue<TGrad>()
	textQueue = QQueue<TText>()

	qimg = QImage()
    #For gray conversion
	ctable = QVector<QRgb>() 
	inicio = QPoint()
    actual = QPoint()
	translating = false
	backPos = QPointF()
	DRAW_AXIS = false
    DRAW_PERIMETER = false

	linGrad = QLinearGradient()
    
    iniCoorSelected = QPointF()
    endCoorSelected = QPointF()
    onSelection = false  
	
    TRect = namedtuple('TRect', 'rect color id ang fill width')
	TEllipse = namedtuple('TEllipse', 'rect center rx ry color id fill ang')
	TLine = namedTuple('TLine', 'line color width')
	TGrad = namedTuple('TGrad', 'line color color1 width')
	TText = namedTuple('TText', 'pos size color text width')

#signals:
    #void windowSelected(QPointF center, int sizeX, int sizeY);
    #void pressEvent();

    def __init__(self, width, heigth, imgVisor, imgFrame):
        invertedVerticalAxis=false
        W_AXIS = false
        W_PERIMETER = false
        imageScale = 1.0
	
        	if (qimg != NULL)
            imageScale = width/qimg.width()
	
        	else
            	qimg = new QImage(width,height,QImage.Format_Indexed8)
		    qimg.fill(240)
	
        	#Gray color table
        ctable.resize(256)
	    
		for (int i = 0; i < 256; i++)
        		ctable[i] = qRgb(i,i,i)
	
        qimg->setColorTable(ctable)
	    translating = false
	    effWin = win
		QGLFormat f = format()
	
		if (f.sampleBuffers())
			f.setSampleBuffers( true )
			setFormat( f )
			print("Sample Buffers On in QGLWidget")
	
		else
			print("Sample Buffers Off in QGLWidget")

        onSelection = false
		show()
        
    def mousePressEvent(mouseEvent):
        if ( mouseEvent.button() == Qt.LeftButton )	
            iniCoorSelected.setX(mouseEvent.x())
            iniCoorSelected.setY(mouseEvent.y())
            endCoorSelected.setX(mouseEvent.x())
            endCoorSelected.setY(mouseEvent.y())

            onSelection = true
            emit pressEvent()

	
    def mouseMoveEvent(mouseEvent):
        endCoorSelected.setX(mouseEvent.x())
        endCoorSelected.setY(mouseEvent.y())
    
    def mouseReleaseEvent(mouseEvent):
        if (mouseEvent.button() == Qt.LeftButton)
            emit windowSelected((iniCoorSelected+endCoorSelected)/2, abs(endCoorSelected.x()-iniCoorSelected.x()),abs(endCoorSelected.y()-iniCoorSelected.y()))
        onSelection = false

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

};

#endif
