import json
import paths as myPaths
from flask_socketio import SocketIO, send, emit
from datetime import timedelta
import time

class VisionData:
    data = []
    startTime = None
    timer = None
    interval = None

    def setTimer(self, time):
        if self.timer is None:
            self.timer = time

    def getTimer(self):
        return self.timer
    
    def setInterval(self, time):
        if self.interval is None:
            self.interval = time

    def setStartTime(self, time):
        if self.startTime is None:
            self.startTime = time

    def getStartTime(self):
        return self.startTime

    def setData(self, data):
        self.data = data

    def getData(self):
        return self.data

    def pushData(self, classes, cc_array, socketio, detect):
        if (time.time()-self.interval) > 1:
            st = str(timedelta(seconds=len(self.data)+1))
            objects = ""
            for c in classes:
                objects = objects+cc_array[c].get("name_rus")+", "
            record = {
                "time": st,
                "objects": objects[:-2]
            }
            self.data.append(record)
            if detect in classes:
                socketio.emit("onScreen", {'onScreen': True, "name": cc_array[detect].get("name_rus")})
            else:
                socketio.emit("onScreen", {'onScreen': False, "name": cc_array[detect].get("name_rus")})
            socketio.emit("transcripts", record)
            self.interval = time.time()

    def writeFile(self):
        if self.data:
            with open(f"{myPaths.TRANSCRIPTSATH}/{self.startTime}.json", "w", encoding="utf-8") as file:
                json.dump(self.data, file, ensure_ascii=False, indent=4)
    
    def clear(self):
        self.data = []
        self.startTime = None
        self.timer = None
        self.interval = None

