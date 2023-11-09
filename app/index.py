from flask import Flask, Response, jsonify, request, send_file
import cv2
import json
from flask_cors import CORS
import os
from classes import Camera, VisionData
from vision import gen_frames
import paths as myPaths
from flask_socketio import SocketIO

app = Flask('Drone')
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = False
app.config['CORS_HEADERS'] = ['Content-Type']
cors = CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
camera = Camera()
vision_data = VisionData()


@app.route('/camera')
def video_img_stream():
    return Response(gen_frames(camera, vision_data, socketio), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/set_params', methods=["POST"])
def videoSetParams():
    try:
        preload = {
            "10.3.93.10": "../preload/project1.mp4",
            "10.3.93.11": "../preload/project2.mp4",
            "10.3.93.12": "../preload/project1-fast.mp4",
            "10.3.93.13": "../preload/project2-fast.mp4"
        }
        data = request.get_json()
        camera.clear()
        vision_data.clear()
        if preload.get(data.get('link')) is not None:
            newCamera = cv2.VideoCapture(preload.get(data.get('link')))
        else:
            if data.get("auth"):
                newCamera = cv2.VideoCapture(f"rtsp://{data.get('login')}:{data.get('password')}@{data.get('link')}")
            else:
                newCamera = cv2.VideoCapture(f"rtsp://{data.get('link')}") 
        # newCamera = cv2.VideoCapture(1)
        camera.setCamera(newCamera)
        newModel = data.get("model")
        camera.setFrameRate(data.get("frame"))
        camera.setModel(newModel, data.get('model_settings'), data.get("detect_list"), data.get("detect_object"))
        if newCamera.isOpened():
            return "Success", 200
        else:
            return "Failed to connect camera", 404
    except Exception as e:
        print(e)
        return "Failed", 500


@app.route('/save_connect', methods=["POST"])
def saveConnect():
    try:
        requestData = request.get_json()
        data = None
        with open(myPaths.CONNECTSPATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        with open(myPaths.CONNECTSPATH, "w", encoding="utf-8") as f:
            data.append(requestData)
            json.dump(data, f, ensure_ascii=False, indent=4)  
        return "Success", 200
    except Exception as e:
        print(e)
        return "Failed", 500 
    

@app.route('/delete_connect', methods=["POST"])
def deleteConnect():
    try:
        requestData = request.get_json()
        data = None
        with open(myPaths.CONNECTSPATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        with open(myPaths.CONNECTSPATH, "w", encoding="utf-8") as f:
            data.remove(requestData)
            json.dump(data, f, ensure_ascii=False, indent=4)  
        return "Success", 200
    except Exception as e:
        print(e)
        return "Failed", 500 


@app.route('/get_models', methods=["GET"])
def getModels():
    data = None
    with open(myPaths.MODELPATH, encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


@app.route('/get_connects', methods=["GET"])
def getConnects():
    data = None
    with open(myPaths.CONNECTSPATH, encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


@app.route("/off_camera", methods=["POST"])
def offCamera():
    camera.off()
    vision_data.writeFile()
    camera.clear()
    vision_data.clear()
    return "Success", 200


@app.route("/get_model_class/<filename>")
def getModelCC(filename):
    data = None
    path = f"{myPaths.MODELCCPATH}/{filename}.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


@app.route('/get_video_list', methods=["GET"])
def getVideos():
    page = int(request.args.get("page", default="1"))
    limit = int(request.args.get("limit", default="6"))
    data = []
    for f in os.listdir(myPaths.VIDEO_PATH):
        name, ext = os.path.splitext(f)
        if ext == ".mp4":
            data.append(f)
    data.reverse()
    carriage = (page-1)*limit
    carriage_limit = carriage+limit
    resp = Response(response=json.dumps(data[carriage:carriage_limit]), status=200, mimetype="application/json")
    resp.headers["Access-Control-Expose-Headers"] = "X-Total-Count" 
    resp.headers["X-Total-Count"] = len(data)
    return resp


@app.route('/video/<filename>')
def display_video(filename):
    return send_file(f"{myPaths.VIDEO_PATH}/{filename}", as_attachment=False) , 200


@app.route('/delete_video', methods=["POST"])
def deleteVideo():
    try:
        requestData = request.get_data().decode("utf-8")
        os.remove(f"{myPaths.VIDEO_PATH}/{requestData}")
        transcript = f"{requestData.split('mp4')[0]}json"
        os.remove(f"{myPaths.TRANSCRIPTSATH}/{transcript}")
        return "Success", 200
    except Exception as e:
        print(e)
        return "Failed", 500 


@app.route("/get_transcript/<filename>")
def get_transcript(filename):
    data = None
    path = f"{myPaths.TRANSCRIPTSATH}/{filename}"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


if __name__ == "__main__":
    socketio.run(app, use_reloader=False, debug=app.config['DEBUG'], host="127.0.0.1", port=5000)
    # socketio.run(app, use_reloader=False, debug=app.config['DEBUG'], host="10.3.93.8", port=5000)
