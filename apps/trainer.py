import re
import os
import cv2
import time
import glob
from deepface import DeepFace
from config import DB_PATH
from service.logger_config import logger, sec_logger


def show_dataset_dirs():
    """Display folders with names from the dataset."""
    print("\nList of trusted persons:")
    folders = [item for item in os.listdir(DB_PATH) if os.path.isdir(os.path.join(DB_PATH, item))]
    if folders:
        for folder in folders:
            print(folder)
    else:
        print("The list is currently empty.")


def is_valid_folder_name(name: str) -> bool:
    """Check for prohibited items and Cyrillic characters."""
    if not name or name.strip() == '':
        return False
    forbidden_chars = re.compile(r'[<>:"/\\|?*а-яА-ЯёЁ\s]')
    return not bool(forbidden_chars.search(name))


def photo_session():
    """Photoshoot"""

    person_name = input("Enter your name in English: ")
    save_dir = os.path.join(DB_PATH, person_name)

    if is_valid_folder_name(person_name):
        os.makedirs(save_dir, exist_ok=True)
    else:
        print("You entered a name with invalid characters!")
        return

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Create a window in advance and drag it to the foreground
    cv2.namedWindow("Record", cv2.WINDOW_AUTOSIZE)
    cv2.setWindowProperty("Record", cv2.WND_PROP_TOPMOST, 1)

    # Timer for the interval between shots
    last_photo_time = time.time()
    photo_interval = 2.5
    photo_count = 0
    total_photos = 8  # How many photos to take

    # Flag to enable flash for one frame
    flash_active = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # If the flash flag is triggered, fill the screen with white
        if flash_active:
            display_frame = frame.copy()
            display_frame.fill(255)  # 255 — white color in all channels
            flash_active = False  # Turn it off immediately so that it only flashes for 1 frame
        else:
            display_frame = frame.copy()
            # Text in English so that the OpenCV font can display it!
            cv2.putText(display_frame, f'LOOK AT THE CAMERA! {photo_count}/{total_photos}', (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Record", display_frame)

        current_time = time.time()
        if current_time - last_photo_time >= photo_interval:
            last_photo_time = current_time

            faces = DeepFace.extract_faces(img_path=frame, detector_backend='opencv', enforce_detection=False)

            if faces and len(faces) > 0:
                face_img = faces[0]['face']
                face_img = (face_img * 255).astype('uint8')

                photo_path = os.path.join(save_dir, f"face_{photo_count}.jpg")
                cv2.imwrite(photo_path, face_img)
                logger.info(f"[DATASET] Photo saved: {photo_path}")

                photo_count += 1
                flash_active = True  # Turn on the flash for the next shot

        # AUTO-EXIT: If we have collected the required number of photos, we end the session
        if photo_count >= total_photos:
            logger.info(f"\n[DATASET] DB for {person_name} has been created successfully!")

            # Delete previous pkl-file
            cache_pattern = os.path.join(DB_PATH, "ds_model_vggface*.pkl")
            found_caches = glob.glob(cache_pattern)
            for cache_file in found_caches:
                try:
                    os.remove(cache_file)
                    print(f"[DATASET] Successfully auto-deleted old cache: {os.path.basename(cache_file)}")
                except Exception as e:
                    print(f"[DATASET] Error auto-deleting cache: {e}")

            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# photo_session()
