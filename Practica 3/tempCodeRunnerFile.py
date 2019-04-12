#imageAux = np.zeros((240, 320), np.uint8)
                        imageAux = self.mapObjects[self.objectList.currentText()]
                        imageAux = np.array(imageAux.getScales()[0], dtype=np.uint8)