from datetime import datetime, timedelta
import numpy as np
import cv2
from ultralytics import YOLO
import json
from os import path
import json
import time


def gen_frames(camera):
    try:
        currentCamera = camera.getCamera()
        currentModel = camera.getModel()
        frame_width = int(currentCamera.get(3))
        frame_height = int(currentCamera.get(4))
        size = (frame_width, frame_height)
        cc_array = []
        timeNow = datetime.now().strftime("%d.%m.%Y_%H:%M")
        timerStart = time.time()
        parent_dir = path.dirname(path.abspath(__file__))
        with open(path.join(parent_dir, "..", "models_cc", f"{currentModel}.json"), encoding="utf-8") as f:
            cc_array = json.load(f)
        # camera.setVideo(cv2.VideoWriter(
        #     f'./video/{timeNow}.mp4', cv2.VideoWriter_fourcc(*'avc1'), 24, size))
        # camera.setVideo(cv2.VideoWriter(
        #     f'./video/{timeNow}.mp4', cv2.VideoWriter_fourcc(*'hev1'), 24, size))
        model = YOLO(currentModel)
        timeStart = time.time()
        while (currentCamera.isOpened()):
            success, frame = currentCamera.read()
            if not success:
                break
            else:
                results = model(frame, device="mps", conf=0.33)
                result = results[0]
                bboxes = np.array(result.boxes.xyxy.cpu(), dtype="int")
                classes = np.array(result.boxes.cls.cpu(), dtype="int")
                if (time.time()-timeStart) > 1:
                    timeStart = writeTranscripts(timeNow, classes, cc_array, time.time()-timerStart)
                for cls, bbox in zip(classes, bboxes):
                    rgb_color = cc_array[cls].get("color_rgb")
                    (x, y, x2, y2) = bbox
                    cv2.rectangle(frame, (x, y), (x2, y2), rgb_color[::-1], 2)
                    cv2.putText(
                        frame, cc_array[cls].get("name_rus"), (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 1, rgb_color[::-1], 2)
                # camera.getVideo().write(frame)
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        # Возможно здесь картинку вывести трансляция прекращена
    except Exception as e:
        print(e)
        return


def writeTranscripts(name, classes, cc_array, timer):
    try:
        parent_dir = path.dirname(path.abspath(__file__))
        data = []
        with open(path.join(parent_dir, "..", "transcripts", f"{name}.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as e:
        print(e)
    finally:
        timer = str(timedelta(seconds=int(timer)))
        objects = ""
        for c in classes:
            objects = objects+cc_array[c].get("name_rus")+", "
        record = {
            "time": timer,
            "objects": objects[:-2]
        }
        with open(path.join(parent_dir, "..", "transcripts", f"{name}.json"), "w", encoding="utf-8") as f:    
            data.append(record)
            json.dump(data, f, ensure_ascii=False, indent=4)  
        return time.time()
 
