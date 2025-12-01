from flask import Flask, request, jsonify
import requests
import time
import threading

# =============================
# CONFIG
# =============================
DEVICE_ID = "bus001"   # Change per device

CLOUD_FN = "https://us-central1-smartbus-f22a4.cloudfunctions.net/iotUpload"

# Latest counts from MAC YOLO
people_entered = 0
people_exited = 0

UPLOAD_INTERVAL = 30  # seconds – can adjust

app = Flask(__name__)

# ======================================
# 1️⃣ MAC → PI receiver
# ======================================
@app.route("/update", methods=["POST"])
def update_counts():
    global people_entered, people_exited

    data = request.json
    if not data:
        return jsonify({"error": "No JSON"}), 400

    # IMPORTANT: Get the values the MAC code sends
    people_entered = data.get("peopleEntered", people_entered)
    people_exited = data.get("peopleExited", people_exited)

    print(f"[PI] Updated → Entered={people_entered}, Exited={people_exited}")
    return jsonify({"status": "ok"}), 200


# ======================================
# 2️⃣ PERIODIC UPLOADER → Firebase
# ======================================
def upload_loop():
    while True:
        payload = {
            "deviceId": DEVICE_ID,
            "timestamp": int(time.time()),
            "payload": {
                "entered": people_entered,
                "exited": people_exited
            }
        }

        try:
            r = requests.post(CLOUD_FN, json=payload, timeout=5)
            print(f"[UPLOAD] ({r.status_code}) {payload}")
        except Exception as e:
            print("[UPLOAD ERROR]", e)

        time.sleep(UPLOAD_INTERVAL)


# ======================================
# MAIN
# ======================================
if __name__ == "__main__":
    print("[PI] SmartBus Receiver + Firebase Uploader running...")

    threading.Thread(target=upload_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
