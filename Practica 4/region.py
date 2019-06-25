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
        count = 0
        print("length of frontier = ", len(self.frontierPointsList))
        print("Size of region: ", self.currentCount)
        for i in self.frontierPointsList:
            if i[2] == regionID:
                count += 1
        return count/len(self.frontierPointsList)

    def percentageOfBorder(self, cannyBorder, regionID):
        countBorder = 0
        countRegion = 0
        for i in self.frontierPointsList:
            if i[2] == regionID:
                countRegion += 1
                if cannyBorder[i[0]][i[1]] == 255:
                    countBorder += 1
        if countBorder == 0:
            return 1
        return countRegion/countBorder

    def regionSize(self):
        return self.currentCount

    def regionsInBorder(self):
        output = []
        for i in self.frontierPointsList:
            if i[2] not in output:
                output.append(i[2])
        return output

    def returnFrontier(self):
        return self.frontierPointsList

    def mergeRegion(self, region):
        self.frontierPointsList + region.returnFrontier()
        self.currentCount += region.currentCount
        self.currentTotalGray += region.currentTotalGray
        self.calcAverage()

    def calcAverage(self):
        if self.avgGrey == 0:
            self.avgGrey = self.currentTotalGray / self.currentCount

    def returnAverage(self):
        return self.avgGrey