import sys
import os
import cv2
import time
import requests
import numpy as np
from ultralytics import YOLO
from config import yolo8n_model, DB_PATH, ALERT_IMG_PATH, CAMERA_IP

# Loading the model (the nano version is the fastest)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from service.net_bridge import send_angles_to_esp

model = YOLO(yolo8n_model)

CAMERA_URL = CAMERA_IP
current_angle_x = 90
current_angle_y = 90


def test_mjpeg_bytes():
    """
    Option #1: Reading a pure MJPEG stream via bytes (requests).
    This is the most stable option for Windows and doesn't depend on system codecs.
    """
    global current_angle_x, current_angle_y
    print("[TEST] Running Method #1 (Clean Bytes)...")

    try:
        stream = requests.get(CAMERA_URL, stream=True, timeout=5)
        if stream.status_code != 200:
            print("❌ Error: Camera returned status", stream.status_code)
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return

    print("✅ The network connection is open. Let's grab some footage...")
    bytes_data = b''

    for chunk in stream.iter_content(chunk_size=1024):
        bytes_data += chunk
        a = bytes_data.find(b'\xff\xd8')
        b = bytes_data.find(b'\xff\xd9')

        if a != -1 and b != -1:
            jpg = bytes_data[a:b + 2]
            bytes_data = bytes_data[b + 2:]

            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                continue

            # Run through the neural network and send
            process_frame_and_aim(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


def test_opencv_ffmpeg():
    """
    Option #2: Reading via the built-in OpenCV video capture engine with the FFMPEG codec.
    The classic one-line method.
    """
    print("[TEST] Running method No. 2 (OpenCV + FFMPEG)...")
    cap = cv2.VideoCapture(CAMERA_URL, cv2.CAP_FFMPEG)

    if not cap.isOpened():
        print("❌ Error: OpenCV failed to open stream!")
        return

    print("✅ OpenCV connected to the camera.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ The frame is empty or the stream is interrupted.")
            break

        process_frame_and_aim(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()


def process_frame_and_aim(frame):
    """Common frame processor for both methods."""
    global current_angle_x, current_angle_y

    height, width, _ = frame.shape
    center_x, center_y = width // 2, height // 2

    # Looking for people through YOLO.
    results = model.predict(frame, verbose=False)

    for r in results:
        for box in r.boxes:
            if int(box.cls) == 0:  # Человек
                x1, y1, x2, y2 = map(int, box.xyxy.cpu().numpy()[0])
                target_x = x1 + (x2 - x1) // 2
                target_y = y1 + (y2 - y1) // 3

                # Mathematics of angles
                error_x = target_x - center_x
                error_y = target_y - center_y

                if abs(error_x) > 40: current_angle_x += int(error_x * 0.03)
                if abs(error_y) > 40: current_angle_y -= int(error_y * 0.03)

                current_angle_x = max(0, min(180, current_angle_x))
                current_angle_y = max(0, min(180, current_angle_y))

                # Send the corners to the power board
                send_angles_to_esp(current_angle_x, current_angle_y, laser_on=0)

                # Drawing a sight
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.circle(frame, (target_x, target_y), 5, (0, 0, 255), -1)

    cv2.drawMarker(frame, (center_x, center_y), (255, 255, 255), cv2.MARKER_CROSS, 20, 2)
    cv2.imshow("TEST Wi-Fi AIM", frame)


if __name__ == "__main__":
    # test_mjpeg_bytes()  # Running a test through bytes
    test_opencv_ffmpeg()  # Running the test via OpenCV FFMPEG
