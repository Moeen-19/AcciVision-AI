# 🚨 Real-Time Accident Detection & Alert System (with Web Dashboard)

This project implements an **AI-powered accident detection and alert system** that uses **video streams** (CCTV/RTSP/local camera) to detect potential accidents in real time.  

When an accident is detected, the system:
- Captures a **snapshot** from the video feed,
- Logs the **timestamp**,
- Updates a **live web dashboard** accessible to emergency responders anywhere via a secure URL.

---

## 🧠 Key Features

✅ **End-to-End Deep Learning Pipeline**
- CNN + LSTM model trained on accident vs. normal driving videos  
- Extracts temporal (frame-sequence) features  

✅ **Real-Time Detection**
- Works with local webcam or RTSP CCTV streams  
- Low-latency inference optimized for mini-computers or Raspberry Pi  

✅ **Instant Alert System**
- Saves snapshots & timestamps  
- Sends configurable Twilio SMS alerts (optional)  

✅ **Live Web Dashboard**
- Flask-powered dashboard showing latest detected accidents  
- Can be made publicly accessible via **LocalTunnel** or hosted on cloud  

✅ **Portable Deployment**
- Works on Windows, Linux, Raspberry Pi  
- Supports automatic startup on boot  

---

## 🧩 Project Structure

AcciVision-AI/
│
├──main.ipynb
├──model_cnn_lstm.py
├──camera_config.json
├──models.py
├── app.py                         # Flask app with auth, routing, dashboard
├── real_time_inference.py         # Accident detection engine (multi-stream capable)
├── stream_handler.py              # Handles video stream input (local/webcam/RTSP)
├──dataset
    ├──preprocessed
	├──accident
	    ├──accident_clip_10528.npy # from 0 to 10528	
	├──normal
	    ├──normal_clip_13680.npy # from 0 to 13680
    ├──train
	├──accident
	    ├──Accident.mp4
	├──normal
	    ├──Normal.mp4
├──logs
    ├──events.json
├──model
├──snapshots	
├── templates/                     # HTML pages (Jinja2 templates)
     ├── dashboard.html             # Main dashboard
     ├──login.html
     ├──register.html
     ├──approve_users.html
     ├──analytics.html
├──utils
    ├──__init__.py
    ├──dataset_preparation.py
    ├──stream_handler.py

├── requirements.txt               # Python dependencies
└── README.md
 

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Moeen-19/Accident-Detection-System.git
cd Accident-Detection-System
```
---

### 2️⃣ Create and Activate Virtual Environment

python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```
---

## 📀 Dataset Preparation

You’ll need accident and normal driving videos.
You can collect them from:

Kaggle datasets (e.g., "Car Accident Video Dataset", "A3D Accident Dataset")
YouTube driving footage clips (for normal driving)
Local CCTV or dashcam recordings. # the project already has dataset for normal driving and accident

Organize them like this:

dataset/train/accident/Accident.mp4  
dataset/train/normal/Normal.mp4

Then preprocess:

```bash
python utils/dataset_preparation.py
```
This extracts frame sequences (each of length 16) and saves them as .npy files in:
dataset/preprocessed/accident/
dataset/preprocessed/normal/

---

## 🧠 Model Training

You can train the CNN+LSTM model directly from main.ipynb:
```bash
# Open dataset_preparation.py in VS Code.
# Run the script to extract frame sequences from videos.
# Open main.ipynb in Jupyter or VS Code.
# Run all cells — this will:
# Load and preprocess the data,
# Train the model for 25 epochs,
# Save it as accident_detector_cnn_lstm.h5.
```
Alternatively, you can integrate additional datasets and fine-tune the model later

---

## 🚦 Real-Time Detection

Once your model is trained:
Add the camera configuration to camera_config.json:

```json
{
    "cameras": [
        {
            "name": "Main Camera",
            "url": "rtsp://username:password@camera-ip/stream",
            "username": "username",
            "password": "password"
        }
    ]
}
```
You can connect:
    - Local webcam (cv2.VideoCapture(0)), or
    - RTSP CCTV feed: cap = cv2.VideoCapture("rtsp://username:password@camera-ip/stream")

Then run the real-time inference script:

```bash
python real_time_inference.py 
```

When an accident is detected:

    -A snapshot is saved to /snapshots
    -The dashboard updates automatically

## 🧭 Web Dashboard

Start your dashboard:

```bash
python app.py 
```
Note:
    - Change the IP address in app.py to your local IP address.
    - Change the admin username and password in case you want to use different credentials.
    - Register new users from the dashboard.
    - Approve new users from the dashboard via the "Approve Users" page. It can only be accessed by the admin user login.
    - Users must be approved before logging in. 

Open:

```bash
http://localhost:5000
```

You’ll see a live gallery of accident snapshots with timestamps.

---

## 🌍 Making Dashboard Public (LocalTunnel)

To make your dashboard accessible to emergency responders online:

```bash
lt --port 5000 --subdomain accidentalert
```
---

You’ll get a public URL like:

```bash
https://accidentalert.loca.lt
```
---

Share this link with responders — they can view the dashboard from any device.

⚠️ The tunnel remains live only while your terminal is running.
For permanent access, run LocalTunnel as a background service (see below).

---

## 🧰 Windows Auto-Startup (Optional)

To ensure your system auto-starts the detection + dashboard on every boot:

Create a start_accident_service.bat:

```bash
@echo off
cd /d "C:\AccidentSystem"
call venv\Scripts\activate
start "" python app.py
timeout /t 10
start "" lt --port 5000 --subdomain accidentalert
exit

```
---

### 4️⃣ Configure Task Scheduler

Then use Windows Task Scheduler:

```bash
# Create Task → “At system startup”
# Set Action → “Start a program” → point to the .bat file
# Enable “Run whether user is logged on or not”
```
Your system now auto-starts the detection + dashboard on every boot.

---

## 🔧 Recommended Deployment Setup

| Component         | Device                   | Description                                        |
|------------------|--------------------------|----------------------------------------------------|
| Detection Engine | Raspberry Pi / Mini PC   | Runs the trained TensorFlow model and handles real-time video stream inference |
| Dashboard        | Same device or Cloud VM  | Flask app displaying the live accident detection dashboard |
| Exposure         | LocalTunnel / Ngrok      | Provides public access to the dashboard (temporary or persistent tunnels) |
| Auto-Retraining  | Local machine or server  | Runs `main.ipynb` monthly (can be scheduled via Task Scheduler or cron) |
| Admin Approval   | Web dashboard            | Admin must manually approve new user registrations via login interface |

---

## ⚙️ Troubleshooting

| Issue                                                    | Solution                                                                 |
|----------------------------------------------------------|--------------------------------------------------------------------------|
| `OSError: Unable to open file (file signature not found)` | Model file might be corrupted — re-run the training in `main.ipynb` to regenerate `.h5` |
| Dashboard not updating                                   | Ensure `real_time_inference.py` is running and writing to `logs/events.json` |
| Snapshots not showing in dashboard                       | Check that images are saved in `/snapshots` and filenames match logs     |
| Tunnel disconnects                                       | Restart LocalTunnel or configure it as a background service              |
| Login system lets anyone in                              | Ensure admin approval is enabled and users have `is_approved=True`       |
| Feedback not updating dataset                            | Verify `handle_feedback()` is moving `.npy` files to correct folder      |
| Model predictions are poor                               | Add more training data, improve preprocessing, or retrain the model      |
| Disk space fills up over time                            | Periodically archive or delete old snapshots and logs                    |

---

## 🧾 License

This project is open-source under the MIT License — free to use and modify for research, educational, or public safety purposes.

## 🧑‍💻 Contributors

<Moeen G. Shaikh> — Lead Developer, Model Optimization & System Design
<Zeenat G. Shaikh> — Frontend, UI Design & Analytics functionality 
---

## 🌟 Acknowledgments

Special thanks to:
- **[Webadvisor](https://www.kaggle.com/webadvisor)** for the original [*Real-Time Anomaly Detection in CCTV Surveillance*](https://www.kaggle.com/datasets/webadvisor/real-time-anomaly-detection-in-cctv-surveillance) dataset, which was used to create a custom dataset for training and testing.
- Open-source datasets and research on accident detection.
- TensorFlow, OpenCV, and Flask communities.
- Developers contributing to LocalTunnel for open APIs.

> This project is built with the goal of supporting public safety and faster emergency response through AI.

---