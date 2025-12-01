# 🚍 IOT Crowd Management & Prediction

Real-time crowd monitoring and short-term prediction for public buses using **YOLOv11n**, **IoT sensors**, and a **Firebase-backed pipeline**.

This project is part of our SmartBus system and focuses on:
- Detecting passengers entering/exiting using a camera.
- Logging occupancy data into the cloud.
- Predicting the bus crowd level for the **next 2 hours**.


---

## 🧩 High-Level Architecture

1. **Edge Device + Camera (YOLOv11n)**
   - Runs a lightweight YOLOv11n model on a bus-mounted device (e.g. Raspberry Pi).
   - Tracks each person as they cross entry/exit lines.
   - Maintains counters for:
     - `peopleEntered`
     - `peopleExited`
     - `currentOnBus`

2. **IoT / Network Bridge**
   - Sends aggregated counts periodically to the backend (e.g., Cloud - Firebase).
   - Data is sent as small JSON payloads.

3. **Firebase Realtime Database **
   - Stores each log with:
     - `timestamp`
     - `peopleEntered`
     - `peopleExited`
     - `currentOnBus`
   - Keeps a clean time-series of occupancy.

4. **Prediction Module (ML)**
   - Reads historical logs from Firebase.
   - Builds time-series features (15-minute slots, time of day, weekday, etc.).
   - Uses a simple ML model (e.g., **K-Nearest Neighbors Regressor**) to predict upcoming occupancy.
   - Generates **2-hour ahead** predictions and writes them back to Firebase.

5. ** Frontend Dashboard**
   - A React/Tailwind dashboard can visualize:
     - Current crowd level.
     - Past logs.
     - 2-hour forecasts.

---

## ✨ Features

- 🧠 **YOLOv11n-based crowd detection**
  - Custom trained on our own bus footage (~150+ labeled images).
  - Robust to bus interior lighting and angles.

- 📊 **Time-series logging**
  - Structured logs stored in Firebase for every time interval.

- 🔮 **2-hour prediction**
  - Predicts future occupancy using recent history.
  - Useful for planning capacity and managing crowding.

- ☁️ **Cloud-connected**
  - Firebase as a simple, low-latency backend.
  - Easy to integrate with dashboards, mobile apps, or other services.

---

## 🛠 Tech Stack

- **Computer Vision**
  - [Ultralytics YOLOv11n](https://docs.ultralytics.com/) for person detection.

- **Backend & Data**
  - Firebase Realtime Database
  - REST API / HTTP JSON uploads

- **Machine Learning**
  - Python
  - `scikit-learn` (KNN Regressor or similar)
  - `numpy`, `pandas` for data handling

- **Frontend**
  - React + Vite
  - Tailwind CSS
  - Recharts / similar charting library

---

## 📁 Project Structure (example)

> Update this section once all files are pushed.

```bash
IOTCrowdManagement-Prediction/
├── edge/                  # YOLO detection + counting scripts
│   └── <yolo_counter.py>
├── backend/               # Firebase
│   └── <uploader.py>
├── prediction/            # ML model training + prediction scripts
│   ├── <train_model.py>
│   └── <predict_next_2_hours.py>
└── README.md
```

🎥 Project Demo
<a href="https://youtu.be/CXEYt82gjqI" target="_blank"> <img src="https://img.youtube.com/vi/CXEYt82gjqI/maxresdefault.jpg" alt="SmartBus Demo Video" style="width:100%; border-radius:12px;"> </a>
