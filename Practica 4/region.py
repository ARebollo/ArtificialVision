import cv2
import numpy as np

class region:
    def __init__(self, id, avgColor, avgGrey, frontierPointsList):
        self.id = id
        self.avgColor = avgColor
        self.avgGrey = avgGrey
        self.frontierPointsList = frontierPointsList 