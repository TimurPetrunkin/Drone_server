import json
import paths as myPath 


class Camera:
    camera = None
    model = None
    video = None
    modelcc = None
    model_settings = None
    model_search_classes = None
    detect_object = None
    frame_rate = None

    def setCamera(self, camera):
        self.camera = camera
        self.isOn = True

    def getCamera(self):
        return self.camera

    def getModelcc(self):
        return self.modelcc
    
    def getSetting(self, setting):
        return self.model_settings.get(setting)
    
    def getDetectObject(self):
        return self.detect_object
    
    def getDetectList(self):
        return self.model_search_classes
    
    def setFrameRate(self, data):
        self.frame_rate = int(data)

    def getFrameRate(self):
        return self.frame_rate
    
    def setModel(self, model, settings, search_classes, detect):
        self.model = model
        with open(f"{myPath.MODELCCPATH}/{model}.json", encoding="utf-8") as f:
            self.modelcc = json.load(f)
            self.model_settings = settings
            self.model_search_classes = search_classes
            self.detect_object = detect

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

    def clear(self):
        self.camera = None
        self.model = None
        self.video = None
        self.modelcc = None