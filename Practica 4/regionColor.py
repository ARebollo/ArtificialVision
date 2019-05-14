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
        #print("currentCount: ", self.currentCount, "avgColor: ", self.avgColor, "regionID: ", self.id)
        self.currentCount += 1
        self.avgColor[0] += values[0]
        self.avgColor[1] += values[1]
        self.avgColor[2] += values[2]
        #print("values: " , values)

    def calcAverage(self):
        for i in range(3):
            #print("color en calcAverage: " , int(self.avgColor[i]/self.currentCount))
            self.avgColor[i] = int(self.avgColor[i]/self.currentCount)

    def returnAverage(self):
        #print("color medio en returnAverage: ", self.avgColor)
        return self.avgColor