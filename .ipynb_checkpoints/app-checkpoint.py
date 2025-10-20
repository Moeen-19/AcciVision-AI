from flask import Flask, render_template
import os, json

app = Flask(__name__, static_folder='snapshots')

@app.route('/')
def dashboard():
    events = []
    log_path = "logs/events.json"
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            events = json.load(f)
    events = sorted(events, key=lambda x: x["timestamp"], reverse=True)
    return render_template("dashboard.html", events=events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
