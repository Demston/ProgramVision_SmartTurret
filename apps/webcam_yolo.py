import cv2
import time
import pygame
from ultralytics import YOLO
from config import yolo8n_model, DB_PATH, ALERT_IMG_PATH, CAMERA_IP, SIREN_SOUND_PATH, ATTACK_SOUND_PATH
from service.face_verifier import verify_face_async
from service.logger_config import logger, sec_logger
from service.net_bridge import send_alert_signal, start_turret_listener, get_turret_state, send_angles_to_esp

# Loading the model (the nano version is the fastest)
model = YOLO(yolo8n_model)

pygame.mixer.init()
# Loading the siren sound
alarm_sound = pygame.mixer.Sound(SIREN_SOUND_PATH)
attack_sound = pygame.mixer.Sound(ATTACK_SOUND_PATH)


def turret_vision():
    """The main function of the turret vision"""

    # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)    # Default PC-camera
    cap = cv2.VideoCapture(CAMERA_IP)   # Wi-Fi camera

    # Find the center of the frame. "A" option
    # width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # center_x, center_y = width // 2, height // 2

    # "Dead zone" in pixels (to prevent the engine from shaking in the center)
    deadzone = 60

    # Anti-spam timer
    unknown_start_time = None
    alert_sent = False
    sound_played = False
    sound_played_combat = False
    last_logged_state = None
    turret_start_time = time.time()
    last_seen_time = time.time()

    current_angle_x = 90
    current_angle_y = 90

    start_turret_listener()   # start a background network listener thread from the module

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (1280, 720))

        # Find the center of the frame. "B" option
        width, height = 1280, 720
        center_x, center_y = width // 2, height // 2

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
                    target_y = y1 + (y2 - y1) // 3  # 2 or 3 - aim for the body (torso)

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

            # Calculate a smooth dynamic step for the X-axis
            if abs(error_x) > 200:
                step_x = 3  # Far away - move faster
            elif abs(error_x) > 100:
                step_x = 2  # Closer - slow down
            else:
                step_x = 1  # Even closer - 1 degree increments

            # X-axis processing
            if abs(error_x) > deadzone:
                if error_x > 0:
                    current_angle_x -= step_x
                else:
                    current_angle_x += step_x

            # Calculate a smooth dynamic step for the Y-axis
            if abs(error_y) > 150:
                step_y = 2  # Far away - move faster
            else:
                step_y = 1  # Closer - 1 degree increments to eliminate shaking

            # Y-axis processing
            if abs(error_y) > deadzone:
                if error_y > 0:
                    current_angle_y -= step_y
                else:
                    current_angle_y += step_y

            # Return the default dead zone for rest in the center of the frame
            deadzone = 40

            # Clamp the angles into safe 0-180 frames for servos
            current_angle_x = max(15, min(165, current_angle_x))
            current_angle_y = max(60, min(120, current_angle_y))

            # ===================================================================

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
                last_seen_time = time.time()

                # Check that more than few seconds have passed since the target was captured
                if unknown_start_time is not None and (time.time() - unknown_start_time > 3.0):
                    if not sound_played:
                        alarm_sound.play()  # alert sound after few seconds
                        sound_played = True

                # If the sound hasn't played yet, it means this is the first moment of switching to attack
                if not sound_played:
                    alarm_sound.play()
                    sound_played = True

                # === ALARM TIMER AND NETWORK BRIDGE LOGIC ===
                if unknown_start_time is None:
                    unknown_start_time = time.time()  # Note the time of the alien's appearance

                # If the alien is in the frame continuously for more than N seconds and the signal has not yet been sent
                elif time.time() - unknown_start_time >= 3.0 and not alert_sent \
                        and (time.time() - turret_start_time > 5.0):
                    cv2.imwrite(ALERT_IMG_PATH, frame)  # Save the current frame to disk
                    send_alert_signal()  # Kicking the bot over the network using our new module.
                    alert_sent = True    # Drop the flag

                # The robot aims and issues commands ONLY if there's an intruder (Logic for future hardware)
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

            # Skip axis errors
            error_x = 0
            error_y = 0

            # Auto return to the center after timeout if the person is out of the frame for more than few seconds
            if time.time() - last_seen_time > 3.0:
                current_angle_x = 90
                current_angle_y = 90
                sound_played = False  # skip the siren

        turret_net_state = get_turret_state()

        if turret_net_state == "CHAOS_FIRE":
            # Hard Attack Mode:
            # In this mode, the turret ignores the deadzone and fires the strobe at full blast.
            # Full Attack Mode: Helmet tracking angles and turn on the laser (laser_on=1)
            if not sound_played_combat:
                pygame.mixer.stop()         # stop the siren
                attack_sound.play()         # launch the attack sound once
                sound_played_combat = True
                sound_played = True
            if best_target:
                send_angles_to_esp(current_angle_x, current_angle_y, laser_on=1)
            else:
                # If there is no target, we don’t turn on the laser and stay in the current position.
                send_angles_to_esp(current_angle_x, current_angle_y, laser_on=0)
            if last_logged_state != "CHAOS_FIRE":
                logger.warning("[TURRET SYSTEM] ATTACK MODE ACTIVE: Simulating 5V supply to the gearbox relay...")
                last_logged_state = "CHAOS_FIRE"

        elif turret_net_state == "ALLOW_GUEST":
            # Remote Trust Mode:
            # Trust Mode: reset the motors exactly to the center (90, 90) and turn off the laser (laser_on=0)
            send_angles_to_esp(90, 90, laser_on=0)
            cv2.putText(frame, "STATUS: GUEST ALLOWED BY USER", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            if last_logged_state != "ALLOW_GUEST":
                logger.warning("[TURRET SYSTEM] TARGET TRUSTED: Targeting commands are blocked remotely.")
                last_logged_state = "ALLOW_GUEST"
            # Reset all sound flags
            sound_played = False
            sound_played_combat = False
            pygame.mixer.stop()

        else:
            # Default GUARD mode:
            # If there's an Alien in the frame (Red label), we target them, but don't turn on the laser yet (laser_on=0)
            # If there's a Friendly One in the frame (Green label), we can either target them or not.
            # Еhe turret will watch everyone, but the laser will only fire on the FIRE command!
            last_logged_state = "GUARD"
            sound_played_combat = False
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

    # Parking the motors before shutting them down
    print("[SYSTEM] Parking turret axes to safe home position (90, 90)...")
    send_angles_to_esp(90, 90, laser_on=0)
    time.sleep(0.5)  # give the motors 0.5 second to reach the center

    cap.release()
    cv2.destroyAllWindows()


# turret_vision()
