from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
import sys

class Window(QMainWindow):
	def __init__(self):
		super().__init__()
		
		self.title = "PyQt5 Image"
		self.top = 100
		self.left = 100
		self.width = 680
		self.height = 500
		
		self.InitWindow()
		
	def InitWindow(self):
		print('1')
		self.label = QLabel(self)
		print('2')
		self.label.setPixMap(QPixmap("/Users/dakolas/anaconda3/pkgs/anaconda-navigator-1.9.6-py37_0/lib/python3.7/site-packages/anaconda_navigator/static/images/anaconda.png"))
		print('3')
		self.label.setGeometry(60, 50, 800, 400)
		
		#self.setWindowIcon(QtGui.QIcon())
		print('4')
		self.setWindowTitle(self.title)
		print('5')
		self.setGeometry(self.top, self.left, self.width, self.height)
		print('6')
		self.show()
		
a = Window()