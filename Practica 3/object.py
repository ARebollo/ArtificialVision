import cv2


class object:
    
    def __init__(self, name, selectedImage):
        self.orb = cv2.ORB_create()
        self.name = name
        self.scaleList = []
        self.keyPointList = []
        self.descriptorList = []
        self.scaleImage(selectedImage)
        self.calculateKpAndDes()

    def renameObject(self, name):
        self.name = name

    def scaleImage(self, image):
        self.scaleList[0] = image
        self.scaleList[1] = cv2.resize(image,0, 1.3, 1.3)
        self.scaleList[1] = cv2.resize(image,0, 0.7, 0.7)

    def calculateKpAndDes(self):
        #TODO Fix
        for i in self.scaleList:
            self.keyPointList[i], self.descriptorList[i] = self.orb.detectAndCompute(i, None)
    
    def calculateMatches(self, descriptors):
        bf = cv2.BFMatcher()
        obtainedMatches = []
        for i in self.descriptorList:
            obtainedMatches.append(bf.knnMatch(descriptors, i, k = 2))
        goodMatches = []
        for i in range(0,2):
            goodMatches[i] = []
            for m, n in obtainedMatches[i]:
                if m.distance < 0.95*n.distance:
                    goodMatches[i].append([m])

        