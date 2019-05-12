import cv2
import numpy as np

class regionColor:
    def __init__(self, id, rectangle, frontierPointsList = [], avgColor = [0,0,0]):
        self.id = id
        self.avgColor = avgColor
        self.frontierPointsList = frontierPointsList
        self.currentCount = 0
        self.rect = rectangle
        
    def addPoint(self, values):
        self.currentCount += 1
        for i in self.avgColor:
            i += values[self.avgColor.index(i)]

    def returnAverage(self):
        for i in self.avgColor:
            i = i/self.currentCount
        return self.avgColor