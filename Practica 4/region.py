import cv2
import numpy as np

class region:
    def __init__(self, id, rectangle, frontierPointsList = [], avgColor = 0, avgGrey = 0):
        self.id = id
        self.avgColor = avgColor
        self.avgGrey = avgGrey
        self.frontierPointsList = frontierPointsList
        self.currentTotalGray = 0
        self.currentCount = 0
        self.rect = rectangle
    def addPoint(self, value):
        self.currentCount += 1
        self.currentTotalGray += value

    def returnAverage(self):
        if self.avgGrey == 0:
            self.avgGrey = self.currentTotalGray / self.currentCount
        return self.avgColor, self.avgGrey