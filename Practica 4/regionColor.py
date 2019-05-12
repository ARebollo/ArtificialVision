import cv2
import numpy as np

class regionColor:
    def __init__(self, id, rectangle, frontierPointsList = [], avgColor = [0,0,0]):
        self.id = id
        self.avgColor = avgColor
        self.frontierPointsList = frontierPointsList
        self.currentCount = 0
        self.rect = rectangle
        
    def addPoint(self, R, G, B):
        self.currentCount += 1
        self.avgColor[0] += R
        self.avgColor[1] += G
        self.avgColor[2] += B

    def returnAverage(self):
        #print(self.avgColor)
        for i in range(3):
            self.avgColor[i] = int(self.avgColor[i]/self.currentCount)
        #print(self.avgColor)
        return self.avgColor