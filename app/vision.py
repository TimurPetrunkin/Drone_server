from datetime import datetime
import numpy as np
import cv2
from ultralytics import YOLO
import time


def gen_frames(camera, data, socketio):
    try:
        currentCamera = camera.getCamera()
        currentModel = camera.getModel()
        frame_width = int(currentCamera.get(3))
        frame_height = int(currentCamera.get(4))
        size = (frame_width, frame_height)
        model = YOLO(currentModel)
        cc_array = camera.getModelcc()
        data.setStartTime(datetime.now().strftime("%d.%m.%Y_%H_%M"))
        camera.setVideo(cv2.VideoWriter(
            f'../video/{data.getStartTime()}.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 24, size))
        conf = camera.getSetting("conf")
        iou = camera.getSetting("iou")
        max_det = camera.getSetting("max_det")
        c_list = camera.getDetectList()
        detect = camera.getDetectObject()
        currentframe = 0
        frameRate = camera.getFrameRate()
        data.setInterval(time.time())
        while (currentCamera.isOpened()):
            ret, frame = currentCamera.read()
            if ret & (currentframe%frameRate==0):
                results = model(frame, device="mps", conf=conf, iou=iou, max_det=max_det, classes=c_list)
                # results = model(frame, device="0", conf=conf, iou=iou, max_det=max_det, classes=c_list)
                result = results[0]
                bboxes = np.array(result.boxes.xyxy.cpu(), dtype="int")
                classes = np.array(result.boxes.cls.cpu(), dtype="int")
                data.pushData(classes, cc_array, socketio, detect)
                for cls, bbox in zip(classes, bboxes):
                    rgb_color = cc_array[cls].get("color_rgb")
                    (x, y, x2, y2) = bbox
                    cv2.rectangle(frame, (x, y), (x2, y2), rgb_color[::-1], 2)
                    cv2.putText(
                        frame, cc_array[cls].get("name_rus"), (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 1, rgb_color[::-1], 2)
                camera.getVideo().write(frame)
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            currentframe += 1
            if ret:
                continue
            else: 
                break
        # Возможно здесь картинку вывести трансляция прекращена
    except Exception as e:
        print(e)
        return