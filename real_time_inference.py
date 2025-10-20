# real_time_inference.py

import json
from utils.stream_handler import StreamHandler

# Load camera config
with open("camera_config.json", "r") as f:
    cameras = json.load(f)

# Start a thread per camera
handlers = []

for cam in cameras:
    handler = StreamHandler(
        camera_id=cam["id"],
        camera_name=cam["name"],
        rtsp_url=cam["rtsp_url"]
    )
    handler.start()
    handlers.append(handler)

print("✅ All camera streams started. Press Ctrl+C to stop.")

# Keep main thread alive
try:
    while True:
        pass
except KeyboardInterrupt:
    print("🔻 Stopping all streams...")
    for h in handlers:
        h.stop()
