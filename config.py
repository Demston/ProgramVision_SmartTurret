import os
from dotenv import load_dotenv

# === APPLICATION SETTINGS ===
script_dir = os.path.dirname(os.path.abspath(__file__))

yolo8n_model = os.path.join(script_dir, "models/yolov8n.pt")                            # usual yolo model
DB_PATH = os.path.join(script_dir, "dataset")                                           # dataset photo path
ALERTS_DIR = os.path.join(script_dir, "alerts")                                         # strange photo path
ALERT_IMG_PATH = os.path.normpath(os.path.join(script_dir, "alerts", "alert.jpg"))      # strange photo default name
SOUND_PATH = os.path.join(script_dir, "media/audio/siren_cut.mp3")                      # siren sound path

# === PATHS TO LOGS ===
LOGS_DIR = os.path.join(script_dir, "logs")
SECURITY_LOG = os.path.join(LOGS_DIR, "security_alerts.log")
SYSTEM_LOG = os.path.join(LOGS_DIR, "system_runtime.log")

# === TELEGRAM SETTINGS ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("MY_CHAT_ID")

# === NETWORK BRIDGE SETTINGS ===
LISTEN_PORT = 5006
TURRET_PORT = 5007
LOCALHOST = "127.0.0.1"
ESP_PORT = 8888
ESP_IP = "192.168.1.253"
CAMERA_IP = "http://192.168.1.254:81/stream"
