import socket
import threading
from config import LOCALHOST, LISTEN_PORT, TURRET_PORT, ESP_IP, ESP_PORT
from service.logger_config import logger, sec_logger


# Global turret mode state from TG within the turret process
# Can be: "GUARD" (normal), "ALLOW_GUEST" (skip), "CHAOS_FIRE" (attack)
_current_state = "GUARD"
_state_lock = threading.Lock()


def send_alert_signal():
    """Sends a quick network signal to the bot that a new intruder has appeared."""
    try:
        # Create a fast UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b"NEW_ALERT", (LOCALHOST, LISTEN_PORT))
        sock.close()
        logger.warning("[NET] The NEW_ALERT signal was successfully sent to the bot over the network.")
    except Exception as e:
        logger.error(f"[NET] Failed to send signal to bot: {e}")


def _network_worker():
    """An internal worker that listens endlessly on port 5007"""
    global _current_state

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LOCALHOST, TURRET_PORT))
    logger.info(f"[NET] Turret listener launched on port {TURRET_PORT}...")

    while True:
        try:
            data, _ = sock.recvfrom(1024)
            command = data.decode('utf-8')

            with _state_lock:
                if command == "ALLOW":
                    _current_state = "ALLOW_GUEST"
                    logger.warning("[NET] Received command: TRUST. Turret ignores target.")
                elif command == "FIRE":
                    _current_state = "CHAOS_FIRE"
                    logger.warning("[NET] Command received: ATTACK! Activating peripherals.")

        except Exception as e:
            logger.error(f"[NET] Listener socket error: {e}")


def start_turret_listener():
    """Starts a background thread listening to ports from a TG bot."""
    t = threading.Thread(target=_network_worker, daemon=True)
    t.start()


def get_turret_state() -> str:
    """Returns the current mode received from Telegram."""
    with _state_lock:
        return _current_state


def send_command_to_turret(command: str):
    """The bot sends a text command (ALLOW / FIRE) back to the turret"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(command.encode('utf-8'), (LOCALHOST, TURRET_PORT))
        sock.close()
        logger.warning(f"[NET] Command {command} sent to turret.")
    except Exception as e:
        logger.error(f"[NET] Failed to send command to turret: {e}")


def send_angles_to_esp(angle_x: int, angle_y: int, laser_on: int = 0):
    """Sends calculated YOLO coordinates and laser status directly to the physical ESP32 board via Wi-Fi"""
    try:
        # UDP socket without delays
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Pack the data into a simple string, for example: "90;120;1"
        packet = f"{angle_x};{angle_y};{laser_on}".encode('utf-8')

        sock.sendto(packet, (ESP_IP, ESP_PORT))
        sock.close()
    except Exception as e:
        logger.error(f"[NET] Ошибка отправки пакета на ESP32: {e}")
