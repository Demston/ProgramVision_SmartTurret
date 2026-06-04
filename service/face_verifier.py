import os
import threading
from deepface import DeepFace
from service.logger_config import logger, sec_logger


current_user = "UNKNOWN"  # Here we store the name of the recognized one
lock = threading.Lock()
is_processing = False

miss_counter = 0     # The counter of "non-recognition" in a row
MAX_MISSES = 2       # Number of misses allowed before alarm is triggered (seconds)


def _async_worker(person_crop, db_path):
    global is_processing, miss_counter, current_user
    try:
        # Launch verification. Enforce_detection=False will prevent falls if your face is blurred
        dfs = DeepFace.find(img_path=person_crop, db_path=db_path,
                            enforce_detection=False, silent=True)
        match_name = "UNKNOWN"

        # Check that the list returned is not empty.
        if isinstance(dfs, list) and len(dfs) > 0:
            df = dfs[0]  # Take the first data frame from the list of results
            if not df.empty:  # Check if there is at least one line with a match
                matched_file_path = df['identity'].values[0]  # Extract the path to the first matching photo from the DB
                # The magic of os.path: we take the name of the folder in which this file is located
                match_name = os.path.basename(os.path.dirname(matched_file_path))

        with lock:
            if match_name != "UNKNOWN":
                current_user = match_name
                miss_counter = 0  # Reset the counter once the face has been successfully recognized
            else:
                miss_counter += 1
                # Lose trust only if we accumulate a series of mistakes in a row
                if miss_counter >= MAX_MISSES:
                    current_user = "UNKNOWN"

    except Exception as e:
        # Display an error in the console if it suddenly occurs
        logger.error(f"[TURRET SYSTEM] Biometrics failure: {e}")
        with lock:
            miss_counter += 1
            if miss_counter >= MAX_MISSES:
                current_user = False

    is_processing = False


def verify_face_async(frame, box, db_path):
    global is_processing

    if is_processing:
        return get_auth_status()

    x1, y1, x2, y2 = box
    h, w, _ = frame.shape

    # Force to take the YOLO coordinates in their entirety, simply by protecting from flying off the edges of the screen
    y1_safe, y2_safe = max(0, y1), min(h, y2)
    x1_safe, x2_safe = max(0, x1), min(w, x2)

    # Cut out the silhouette completely - from a distance it will be the head and shoulders,
    # from a close-up it will be the entire height
    person_crop = frame[y1_safe:y2_safe, x1_safe:x2_safe]

    if person_crop.size == 0:
        return get_auth_status()

    is_processing = True
    t = threading.Thread(target=_async_worker, args=(person_crop, db_path), daemon=True)
    t.start()

    return get_auth_status()  # will return the name or "UNKNOWN"


def get_auth_status():
    with lock:
        return current_user
