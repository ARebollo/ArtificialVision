import cv2
import numpy as np

class region:
    def __init__(self, id, frontierPointsList, rectangle, avgColor = 0, avgGrey = 0):
        self.id = id
        self.avgColor = avgColor
        self.avgGrey = avgGrey
        self.frontierPointsList = frontierPointsList
        self.currentTotal = 0
        self.currentCount = 0
        self.rect = rectangle
    def addPoint(self, value):
        self.currentCount += 1
        self.currentTotal += value

    def returnAverage(self):
        return self.avgColor, self.avgGrey