import cv2
import numpy as np

class region:
    def __init__(self, id, rectangle, frontierPointsList = [], avgGrey = int(0)):
        self.id = id
        self.avgGrey = avgGrey
        self.frontierPointsList = frontierPointsList
        self.currentTotalGray = 0
        self.currentCount = 0
        self.rect = rectangle
    def addPoint(self, value):
        self.currentCount += 1
        self.currentTotalGray += value

    def calcAverage(self):
        if self.avgGrey == 0:
            self.avgGrey = self.currentTotalGray / self.currentCount

    def returnAverage(self):
        return self.avgGrey