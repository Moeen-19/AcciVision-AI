import os
import cv2
import json
import numpy as np
from datetime import datetime
from tensorflow.keras.models import load_model
from geopy.geocoders import Nominatim
import geocoder

SEQUENCE_LENGTH = 16
model = load_model("model/accident_detector_cnn_lstm.h5")

# Ensure necessary folders exist
os.makedirs("snapshots", exist_ok=True)
os.makedirs("logs", exist_ok=True)
EVENT_LOG = "logs/events.json"

def log_event(snapshot_path, location):
    """Logs the accident details into a JSON file"""
    event = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "snapshot": os.path.basename(snapshot_path),
        "location": location
    }
    if os.path.exists(EVENT_LOG):
        with open(EVENT_LOG, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(event)
    with open(EVENT_LOG, "w") as f:
        json.dump(data, f, indent=4)
    print("✅ Event logged:", event)

def get_location():
    """Get location using geocoder (IP-based fallback)"""
    try:
        g = geocoder.ip("me")
        if not g.ok:
            return "Unknown location"
        geoLoc = Nominatim(user_agent="accident_detection")
        locname = geoLoc.reverse(g.latlng, language='en')
        return locname.address if locname else "Unknown"
    except Exception:
        return "Unknown"

# Initialize video stream (can replace with RTSP)
cap = cv2.VideoCapture(0)
frames = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_resized = cv2.resize(frame, (224, 224))
    frames.append(frame_resized)

    if len(frames) == SEQUENCE_LENGTH:
        clip = np.expand_dims(np.array(frames), axis=0)
        pred = model.predict(clip)[0]
        label = np.argmax(pred)
        text = "ACCIDENT" if label == 1 else "NO ACCIDENT"
        color = (0, 0, 255) if label == 1 else (0, 255, 0)
        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        if label == 1:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_path = f"snapshots/snapshot_{timestamp}.jpg"
            cv2.imwrite(snapshot_path, frame)
            print("🚨 Accident detected! Snapshot saved at:", snapshot_path)

            location = get_location()
            log_event(snapshot_path, location)

        frames = []

    cv2.imshow("Real-Time Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
