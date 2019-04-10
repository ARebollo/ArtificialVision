import cv2


class ImageObject:
    
    def __init__(self, name, selectedImage, orb):
        self.orb = orb
        self.name = name
        self.scaleList = []
        self.keyPointList = []
        self.descriptorList = []
        self.scaleImage(selectedImage)
        self.calculateKpAndDes()

    def renameObject(self, name):
        self.name = name

    def scaleImage(self, image):
        self.scaleList.append(image)
        self.scaleList.append(cv2.resize(image,dsize = (0,0), fx = 1.3, fy = 1.3)) 
        self.scaleList.append(cv2.resize(image,dsize = (0,0), fx = 0.8, fy = 0.8)) 

    def getScales(self):
        return self.scaleList.copy()

    def calculateKpAndDes(self):
        for i in self.scaleList:
            kp, des = self.orb.detectAndCompute(i, None)
            self.descriptorList.append(des)
            self.keyPointList.append(kp)

    
    def returnKpDes(self):
        valid = True
        for i in self.keyPointList:
            if i is None:
                valid = False
                break
        for i in self.descriptorList:
            if i is None:
                valid = False
                break
        return self.keyPointList, self.descriptorList, valid
 
        