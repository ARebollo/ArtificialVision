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

    def addFrontierPoint(self, value):
        self.frontierPointsList.append(value)

    def percentageOfFrontier(self, regionID):
        pass

    def frontierIsBorder(self, cannyBorder):
        pass

    def regionSize(self):
        return self.currentCount

    def calcAverage(self):
        if self.avgGrey == 0:
            self.avgGrey = self.currentTotalGray / self.currentCount

    def returnAverage(self):
        return self.avgGrey