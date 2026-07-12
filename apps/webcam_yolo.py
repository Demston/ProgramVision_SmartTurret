import cv2
import time
from ultralytics import YOLO
from config import yolo8n_model, DB_PATH, ALERT_IMG_PATH, CAMERA_IP
from service.face_verifier import verify_face_async
from service.logger_config import logger, sec_logger
from service.net_bridge import send_alert_signal, start_turret_listener, get_turret_state, send_angles_to_esp

# Loading the model (the nano version is the fastest)
model = YOLO(yolo8n_model)


def turret_vision():
    """The main function of the turret vision"""

    # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)    # Default PC-camera
    cap = cv2.VideoCapture(CAMERA_IP)   # Wi-Fi camera
    # Find the center of the frame
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    center_x, center_y = width // 2, height // 2
    # "Dead zone" in pixels (to prevent the engine from shaking in the center)
    deadzone = 40

    # Anti-spam timer
    unknown_start_time = None
    alert_sent = False
    turret_start_time = time.time()

    current_angle_x = 90
    current_angle_y = 90

    start_turret_listener()   # start a background network listener thread from the module

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Basic Magic: one-line recognition and rendering
        results = model.predict(frame, verbose=False, stream=True)
        best_target = None
        min_distance = float('inf')  # The initial distance is infinity

        for r in results:
            for box in r.boxes:
                # Get the class ID (0 is always a person in YOLO) without indices [0]
                cls = int(box.cls)
                if cls == 0:  # Human
                    # Frame coordinates - removed extra [0] to prevent code crashes
                    x1, y1, x2, y2 = map(int, box.xyxy.cpu().numpy()[0])

                    # Aiming point (center of object)
                    target_x = x1 + (x2 - x1) // 2
                    target_y = y1 + (y2 - y1) // 3  # aim for the body (torso)

                    # Calculate the distance from the center of the screen to this target (hypotenuse)
                    dist = ((target_x - center_x) ** 2 + (target_y - center_y) ** 2) ** 0.5

                    # If this person is closer to the center than the previous one, we remember him
                    if dist < min_distance:
                        min_distance = dist
                        best_target = (x1, y1, x2, y2, target_x, target_y)

        # DRAWING (for one best candidate only)
        if best_target:
            x1, y1, x2, y2, target_x, target_y = best_target
            # Calculating the error (offset from the center of the screen)
            error_x = target_x - center_x
            error_y = target_y - center_y

            # =========== OUR PHYSICAL CONTROL CHANNEL ===========
            # Smoothness factor (if the motors spin too slowly, increase it to 0.05)
            k = 0.03

            # If the deviation is greater than the dead zone, we smoothly adjust the angles
            if abs(error_x) > deadzone:
                # If the target is on the right (error_x > 0), we need to rotate the turret to the right.
                # Depending on how you attach the motor, this could be either += or -=.
                # Let's start with the standard option:
                current_angle_x += int(error_x * k)

            if abs(error_y) > deadzone:
                # The Y axis in the camera goes from top to bottom, so we invert the sign here
                current_angle_y -= int(error_y * k)

            # We clamp the angles into safe 0-180 frames for servos
            current_angle_x = max(0, min(180, current_angle_x))
            current_angle_y = max(0, min(180, current_angle_y))
            # =======================================================

            # Invoke an asynchronous check. It runs instantly in the background.
            user_name = verify_face_async(frame, (x1, y1, x2, y2), DB_PATH)

            if user_name != "UNKNOWN" and user_name:
                color = (0, 255, 0)  # Green - Yours
                label = f"OWNER: {user_name.upper()} (ACCESS GRANTED)"
                unknown_start_time = None
                alert_sent = False

            else:
                color = (0, 0, 255)  # Red - Alien
                label = "UNKNOWN: TARGET LOCKED"

                # === ALARM TIMER AND NETWORK BRIDGE LOGIC ===
                if unknown_start_time is None:
                    unknown_start_time = time.time()  # Note the time of the alien's appearance

                # If the alien is in the frame continuously for more than N seconds and the signal has not yet been sent
                elif time.time() - unknown_start_time >= 3.0 and not alert_sent \
                        and (time.time() - turret_start_time > 5.0):
                    cv2.imwrite(ALERT_IMG_PATH, frame)  # Save the current frame to disk
                    send_alert_signal()  # Kicking the bot over the network using our new module.
                    alert_sent = True    # Drop the flag

                # Logic for future hardware. The robot aims and issues commands ONLY if there's an intruder
                if abs(error_x) > deadzone:
                    cmd = f"MOVE {'RIGHT' if error_x > 0 else 'LEFT'} by {abs(error_x)} px"
                    cv2.putText(frame, cmd, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # Drawing sight elements
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)      # Frame around the target
            cv2.circle(frame, (target_x, target_y), 5, color, -1)   # Point in the center of the target
            cv2.line(frame, (center_x, center_y), (target_x, target_y), color, 2)   # Guidance line
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        else:
            # If there are no recognized people in the frame, the status is reset
            user_name = "UNKNOWN"
            unknown_start_time = None
            alert_sent = False

        turret_net_state = get_turret_state()

        if turret_net_state == "CHAOS_FIRE":
            # Hard Attack Mode. In the future: send a command to turn on the relay via UDP to the ESP32!
            # In this mode, the turret ignores the deadzone and fires the strobe at full blast.
            # Full Attack Mode: Helmet tracking angles and turn on the laser (1)
            send_angles_to_esp(current_angle_x, current_angle_y, laser_on=1)
            cv2.putText(frame, "STATUS: Telegram FIRE ACTIVE!", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            logger.warning("[TURRET SYSTEM] ATTACK MODE ACTIVE: Simulating 5V supply to the gearbox relay...")

        elif turret_net_state == "ALLOW_GUEST":
            # Remote Trust Mode.
            # In the future: force the turret to reset its motor coordinates to the center (0,0) and stop tracking.
            # Trust Mode: reset the motors exactly to the center (90, 90) and turn off the laser (0)
            send_angles_to_esp(90, 90, laser_on=0)
            cv2.putText(frame, "STATUS: GUEST ALLOWED BY USER", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            logger.warning("[TURRET SYSTEM] TARGET TRUSTED: Targeting commands are blocked remotely.")

        else:
            # Default GUARD mode:
            # If there's an Alien in the frame (Red label), we target them, but don't turn on the laser yet (0).
            # If there's a Friendly One in the frame (Green label), we can either target them or not.
            # Еhe turret will watch everyone, but the laser will only fire on the FIRE command!
            if best_target:
                send_angles_to_esp(current_angle_x, current_angle_y, laser_on=0)
            else:
                # If there is no one in the room, keep the guns in the center
                send_angles_to_esp(90, 90, laser_on=0)

        # Static crosshair in the center of the screen
        cv2.drawMarker(frame, (center_x, center_y), (255, 255, 255), cv2.MARKER_CROSS, 20, 2)
        cv2.imshow("Auto AIM", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


turret_vision()
