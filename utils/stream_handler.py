# utils/stream_handler.py

import cv2
import numpy as np
import os
import json
import time
from datetime import datetime
from threading import Thread
from tensorflow.keras.models import load_model
from geopy.geocoders import Nominatim
import geocoder

SEQUENCE_LENGTH = 16
model = load_model("model/accident_detector_cnn_lstm.h5")

os.makedirs("snapshots", exist_ok=True)
os.makedirs("logs", exist_ok=True)
EVENT_LOG = "logs/events.json"


def get_location():
    try:
        g = geocoder.ip("me")
        if not g.ok:
            return "Unknown location"
        geoLoc = Nominatim(user_agent="accident_detection")
        locname = geoLoc.reverse(g.latlng, language='en')
        return locname.address if locname else "Unknown"
    except:
        return "Unknown"


def log_event(snapshot_path, location, camera_id, camera_name):
    event = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "snapshot": os.path.basename(snapshot_path),
        "location": location,
        "camera_id": camera_id,
        "camera_name": camera_name
    }
    if os.path.exists(EVENT_LOG):
        with open(EVENT_LOG, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(event)
    with open(EVENT_LOG, "w") as f:
        json.dump(data, f, indent=4)
    print(f"✅ Event logged from {camera_name}:", event)


class StreamHandler(Thread):
    def __init__(self, camera_id, camera_name, rtsp_url):
        super().__init__()
        self.camera_id = camera_id
        self.camera_name = camera_name
        self.rtsp_url = rtsp_url
        self.frames = []
        self.running = True

    def reconnect(self):
        print(f"🔄 Reconnecting to {self.camera_name}...")
        time.sleep(2)
        return cv2.VideoCapture(self.rtsp_url)

    def run(self):
        cap = cv2.VideoCapture(self.rtsp_url)

        while self.running:
            if not cap.isOpened():
                cap = self.reconnect()
                continue

            ret, frame = cap.read()
            if not ret:
                print(f"⚠️ Disconnected from {self.camera_name}. Retrying...")
                cap.release()
                cap = self.reconnect()
                continue

            frame_resized = cv2.resize(frame, (224, 224))
            self.frames.append(frame_resized)

            if len(self.frames) == SEQUENCE_LENGTH:
                clip = np.expand_dims(np.array(self.frames), axis=0)
                pred = model.predict(clip)[0]
                label = np.argmax(pred)

                if label == 1:  # Accident
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = f"{self.camera_id}_{timestamp}.jpg"
                    np.save(f"dataset/preprocessed/accident/{base_name}.npy", np.array(self.frames))
                    snapshot_path = os.path.join("snapshots", base_name)
                    cv2.imwrite(snapshot_path, frame)
                    location = get_location()
                    log_event(snapshot_path, location, self.camera_id, self.camera_name)
                    print(f"🚨 Accident detected on {self.camera_name}!")


                self.frames = []

            time.sleep(0.03)  # ~30 FPS

        cap.release()

    def stop(self):
        self.running = False
