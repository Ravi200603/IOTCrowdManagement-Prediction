import requests
import json
import numpy as np
from sklearn.neighbors import KNeighborsRegressor
import time

# ===============================================================
# CONFIG
# ===============================================================
DATABASE_URL = "https://smartbus-f22a4-default-rtdb.firebaseio.com"
BUS_ID = "bus001"

# Paths
LOGS_URL = f"{DATABASE_URL}/smartbus/{BUS_ID}/logs.json"
PRED_URL = f"{DATABASE_URL}/predictions/{BUS_ID}.json"


# ===============================================================
# 1️⃣ Fetch logs from Firebase
# ===============================================================
def fetch_logs():
    r = requests.get(LOGS_URL)
    if r.status_code != 200:
        print("Failed to fetch logs:", r.text)
        return []

    data = r.json()
    if not data:
        return []

    logs = []
    for k, v in data.items():
        logs.append({
            "timestamp": v.get("timestamp", 0),
            "entered": v.get("entered", 0),
            "exited": v.get("exited", 0)
        })

    # sort by timestamp (old→new)
    logs.sort(key=lambda x: x["timestamp"])
    return logs


# ===============================================================
# 2️⃣ Build training rows using: occupancy = entered - exited
# ===============================================================
def build_training_rows(logs):
    rows = []

    for log in logs:
        ts = log["timestamp"]
        dt = time.localtime(ts)

        hour = dt.tm_hour
        minuteSlot = dt.tm_min // 5
        weekday = dt.tm_wday

        occupancy = log["entered"] - log["exited"]

        rows.append({
            "hour": hour,
            "minuteSlot": minuteSlot,
            "weekday": weekday,
            "entered": log["entered"],
            "exited": log["exited"],
            "occupancy": occupancy,
            "timestamp": ts
        })

    return rows


# ===============================================================
# 3️⃣ Train KNN + Predict next 2 hours
# ===============================================================
def run_knn(rows):
    if len(rows) < 5:
        print("Not enough data yet for KNN")
        return {}

    X = []
    y = []

    for i in range(len(rows) - 1):
        r = rows[i]
        next_r = rows[i + 1]

        X.append([
            r["hour"],
            r["minuteSlot"],
            r["weekday"],
            r["entered"],
            r["exited"],
            r["occupancy"]
        ])

        y.append(next_r["occupancy"])

    model = KNeighborsRegressor(n_neighbors=5)
    model.fit(X, y)

    # start from the latest row
    last = rows[-1]
    feat = [
        last["hour"],
        last["minuteSlot"],
        last["weekday"],
        last["entered"],
        last["exited"],
        last["occupancy"]
    ]

    preds = {}

    # 24 future points → next 2 hours
    for i in range(1, 25):
        p = model.predict([feat])[0]

        # clamp reasonable range
        p = max(0, min(100, p))

        preds[f"next_{i*5}min"] = int(p)

        # feed predicted occupancy forward
        feat[-1] = p  # update occupancy

    preds["updatedAt"] = int(time.time())
    return preds


# ===============================================================
# 4️⃣ Upload to Firebase
# ===============================================================
def upload_predictions(preds):
    r = requests.put(PRED_URL, json=preds)
    print("Uploaded predictions:", r.status_code)


# ===============================================================
# MAIN
# ===============================================================
if __name__ == "__main__":
    logs = fetch_logs()

    if len(logs) == 0:
        print("No logs found.")
        exit()

    rows = build_training_rows(logs)
    preds = run_knn(rows)

    if preds:
        upload_predictions(preds)
