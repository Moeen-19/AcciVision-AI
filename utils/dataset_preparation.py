import os
import cv2
import numpy as np
from tqdm import tqdm

def extract_frames(input_dir, output_dir, sequence_length=16, resize=(224,224)):
    os.makedirs(output_dir, exist_ok=True)
    for video_file in os.listdir(input_dir):
        if not video_file.endswith(".mp4"):
            continue
        cap = cv2.VideoCapture(os.path.join(input_dir, video_file))
        frames = []
        success, frame = cap.read()
        while success:
            frame = cv2.resize(frame, resize)
            frames.append(frame)
            success, frame = cap.read()
        cap.release()

        for i in range(0, len(frames) - sequence_length, sequence_length):
            clip = np.array(frames[i:i+sequence_length])
            np.save(os.path.join(output_dir, f"{os.path.splitext(video_file)[0]}_clip_{i}.npy"), clip)
        print(f"Extracted {len(frames)//sequence_length} clips from {video_file}")
