import cv2
import numpy as np

class regionColor:
    def __init__(self, id, rectangle, frontierPointsList = [], avgColor = [int(0),int(0),int(0)]):
        self.id = id
        self.avgColor = avgColor
        self.frontierPointsList = frontierPointsList
        self.currentCount = 0
        self.rect = rectangle
        self.deleted = False
        
    def addPoint(self, values):
        #print("currentCount: ", self.currentCount, "avgColor: ", self.avgColor, "regionID: ", self.id)
        self.currentCount += 1
        self.avgColor[0] += values[0]
        self.avgColor[1] += values[1]
        self.avgColor[2] += values[2]
    
    def addFrontierPoint(self, value):
        self.frontierPointsList.append(value)

    def percentageOfFrontier(self, regionID):
        count = 0
        '''
        print("length of frontier = ", len(self.frontierPointsList))
        print("Size of region: ", self.currentCount)
        print("Id of region = ", self.id)
        '''
        for i in self.frontierPointsList:
            if i[2] == regionID:
                count += 1
        if len(self.frontierPointsList) == 0:
            return 0
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
        self.avgColor[0] += region.avgColor[0]
        self.avgColor[1] += region.avgColor[1]
        self.avgColor[2] += region.avgColor[2]
        self.calcAverage()

    def addFrontierPoint(self, value):
        self.frontierPointsList.append(value)

    def calcAverage(self):
        for i in range(3):
            #print("color en calcAverage: " , int(self.avgColor[i]/self.currentCount))
            self.avgColor[i] = int(self.avgColor[i]/self.currentCount)
    def returnAverage(self):
        #print("color medio en returnAverage: ", self.avgColor)
        return self.avgColor