from ultralytics import YOLO
import cv2
import requests
import time
import uuid

# ==============================
# CONFIG (CHANGE THIS!!)
# ==============================
DEVICE_ID = "bus001"

# 👉 REPLACE THIS with Raspberry Pi IP:
PI_ENDPOINT = "http://10.203.6.2:5000/update"


STREAM_URL = "tcp://10.203.6.2:8000"   # your phone cam
UPLOAD_INTERVAL = 30                              # not used anymore

model = YOLO("yolo11n.pt")

# Counts
entered = 0
exited = 0
entered_ids = set()
exited_ids = set()
last_y = {}
was_above_exit_line = {}

# Lines
LINE_ENTER = 200
LINE_EXIT = 280
EXIT_RESET_MARGIN = 40


# ===========================================
# 🔵 Send YOLO counts → Raspberry Pi
# ===========================================
def send_to_pi(entered, exited):
    payload = {
        "peopleEntered": entered,
        "peopleExited": exited
    }
    try:
        r = requests.post(PI_ENDPOINT, json=payload, timeout=1)
        print("[MAC → PI] Sent:", payload, "| Status:", r.status_code)
    except Exception as e:
        print("[MAC → PI] Failed:", e)


# ===========================================
# YOLO STREAM
# ===========================================
cap = cv2.VideoCapture(STREAM_URL)
if not cap.isOpened():
    print("[ERROR] Cannot open IP camera stream")
    exit()

print("[INFO] YOLO Counter Running on Mac. Press Q to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.resize(frame, (640, 480))
    results = model.track(frame, persist=True)

    # ===========================================
    # PERSON DETECTION + TRACKING
    # ===========================================
    if results and results[0].boxes is not None:
        for box in results[0].boxes:
            cls = int(box.cls[0])
            if model.names[cls] != "person":
                continue

            track_id = int(box.id[0]) if box.id is not None else None
            if track_id is None:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cy = (y1 + y2) // 2

            # Draw
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.circle(frame, (x1 + 10, cy), 5, (0,255,0), -1)

            if track_id not in last_y:
                last_y[track_id] = cy
                was_above_exit_line[track_id] = True
                continue

            prev_y = last_y[track_id]
            last_y[track_id] = cy

            moving_up = cy < prev_y
            moving_down = cy > prev_y

            if cy < LINE_EXIT:
                was_above_exit_line[track_id] = True

            # ENTER
            if (moving_up and 
                prev_y > LINE_ENTER and 
                cy <= LINE_ENTER and 
                track_id not in entered_ids):

                entered += 1
                entered_ids.add(track_id)
                print(f"[ENTER] → {entered}")
                send_to_pi(entered, exited)

            # EXIT
            if (moving_down and 
                was_above_exit_line.get(track_id, True) and 
                prev_y < LINE_EXIT and 
                cy >= LINE_EXIT and 
                track_id not in exited_ids):

                exited += 1
                exited_ids.add(track_id)
                was_above_exit_line[track_id] = False
                print(f"[EXIT] → {exited}")
                send_to_pi(entered, exited)

    # Draw lines
    cv2.line(frame, (0, LINE_ENTER), (640, LINE_ENTER), (0,255,255), 2)
    cv2.line(frame, (0, LINE_EXIT), (640, LINE_EXIT), (255,0,255), 2)

    cv2.putText(frame, f"ENTER: {entered}", (20,40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.putText(frame, f"EXIT :  {exited}", (20,80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow("SmartBus Counter (Mac Only)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
