import cv2


class ImageObject:
    
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
            kp, des = self.orb.detectAndCompute(i, None)
            self.descriptorList.append(des)
            self.keyPointList.append(kp)

    
    def returnKpDes(self):
        return self.keyPointList, self.descriptorList
    
    def calculateMatches(self, descriptors):
        bf = cv2.BFMatcher()
        obtainedMatches = []
        #TODO Add distance to bfMatcher, Hamming distance.
        #TODO Distance is an integer
        #TODO Instead of doing it object by object, mainwindow pulls from each object and matches everything
        for i in self.descriptorList:
            obtainedMatches.append(bf.knnMatch(descriptors, i, k = 2))
        goodMatches = []
        for i in range(0,2):
            goodMatches[i] = []
            for m, n in obtainedMatches[i]:
                if m.distance < 0.95*n.distance:
                    goodMatches[i].append([m])

        return goodMatches
        