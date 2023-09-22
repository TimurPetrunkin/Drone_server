from flask import Flask, Response, jsonify, request, send_file
import cv2
import json
from flask_cors import CORS, cross_origin
import os
import glob
from camera import Camera
from vision import gen_frames
from flask_sock import Sock

app = Flask('Drone')
cors = CORS(app, support_credentials=True)
videoPath = "../video"
transcriptsPath = "../transcripts"
sock = Sock(app)

@app.route('/camera')
@cross_origin()
def video_img_stream():
    return Response(gen_frames(camera), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/set_params', methods=["POST"])
@cross_origin()
def videoSetParams():
    try:
        data = request.get_json()
        if data.get("auth"):
            newCamera = cv2.VideoCapture(f"rtsp://{data.get('login')}:{data.get('password')}@{data.get('link')}")
        else:
            newCamera = cv2.VideoCapture(f"rtsp://{data.get('link')}") 
        # newCamera = cv2.VideoCapture(1)
        camera.setCamera(newCamera)
        newModel = data.get("model")
        camera.setModel(newModel)
        if newCamera.isOpened():
            return "Success", 200
        else:
            return "Failed to connect camera", 404
    except Exception as e:
        print(e)
        return "Failed", 500


@app.route('/save_connect', methods=["POST"])
@cross_origin()
def saveConnect():
    try:
        requestData = request.get_json()
        data = None
        with open('../connects.json', "r", encoding="utf-8") as f:
            data = json.load(f)
        with open('../connects.json', "w", encoding="utf-8") as f:
            data.append(requestData)
            json.dump(data, f, ensure_ascii=False, indent=4)  
        return "Success", 200
    except Exception as e:
        print(e)
        return "Failed", 500 
    

@app.route('/delete_connect', methods=["POST"])
@cross_origin()
def deleteConnect():
    try:
        requestData = request.get_json()
        data = None
        with open('../connects.json', "r", encoding="utf-8") as f:
            data = json.load(f)
        with open('../connects.json', "w", encoding="utf-8") as f:
            data.remove(requestData)
            json.dump(data, f, ensure_ascii=False, indent=4)  
        return "Success", 200
    except Exception as e:
        print(e)
        return "Failed", 500 


@app.route('/get_models', methods=["GET"])
@cross_origin()
def getModels():
    data = None
    with open('../models.json', encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


@app.route('/get_connects', methods=["GET"])
@cross_origin()
def getConnects():
    data = None
    with open('../connects.json', encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


@app.route("/off_camera", methods=["POST"])
@cross_origin()
def offCamera():
    camera.off()
    return "Success", 200


@app.route('/get_video_list', methods=["GET"])
@cross_origin()
def getVideos():
    data = []
    for f in os.listdir(f"{videoPath}"):
        name, ext = os.path.splitext(f)
        if ext == ".mp4":
            data.append(f)
    return jsonify(data)


@app.route('/video/<filename>')
@cross_origin()
def display_video(filename):
    return send_file(f"{videoPath}/{filename}", as_attachment=False) , 200


@app.route('/delete_video', methods=["POST"])
@cross_origin()
def deleteVideo():
    try:
        requestData = request.get_data().decode("utf-8")
        os.remove(f"{videoPath}/{requestData}")
        transcript = f"{requestData.split('mp4')[0]}json"
        os.remove(f"{transcriptsPath}/{transcript}")
        return "Success", 200
    except Exception as e:
        print(e)
        return "Failed", 500 


@app.route("/get_transcript/<filename>")
@cross_origin()
def get_transcript(filename):
    data = None
    path = f"{transcriptsPath}/{filename}"
    if filename == "latest":
        list_of_files = glob.glob(f'{transcriptsPath}/*.json')
        path = max(list_of_files, key=os.path.getctime) 
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


@sock.route('/echo')
def echo(ws):
    while True:
        data = ws.receive()
        ws.send(data)

camera = Camera()

if __name__ == "__main__":
    app.run()
    camera.off()
