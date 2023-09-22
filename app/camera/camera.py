class Camera:
    camera = None
    model = None
    video = None

    def setCamera(self, camera):
        self.camera = camera
        self.isOn = True

    def getCamera(self):
        return self.camera

    def setModel(self, model):
        self.model = model

    def getModel(self):
        return self.model

    def setVideo(self, video):
        self.video = video

    def getVideo(self):
        return self.video

    def off(self):
        if self.video is not None:
            self.video.release()
        if self.camera is not None:    
            self.camera.release()