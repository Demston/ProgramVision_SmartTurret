import socket
import threading
from config import *
from service.logger_config import logger, sec_logger


# Глобальное состояние режима турели от TG внутри процесса турели
# Может быть: "GUARD" (обычный), "ALLOW_GUEST" (пропустить), "CHAOS_FIRE" (атака)
_current_state = "GUARD"
_state_lock = threading.Lock()


def send_alert_signal():
    """Отправляет быстрый сетевой сигнал боту, что появился новый нарушитель"""
    try:
        # Создаем быстрый UDP сокет
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b"NEW_ALERT", (LOCALHOST, LISTEN_PORT))
        sock.close()
        logger.warning("[NET] Сигнал NEW_ALERT успешно отправлен боту по сети.")
    except Exception as e:
        logger.error(f"[NET] Не удалось отправить сигнал боту: {e}")


def _network_worker():
    """Внутренний воркер, который бесконечно слушает порт 5007"""
    global _current_state

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LOCALHOST, TURRET_PORT))
    logger.info(f"[NET] Слушатель турели запущен на порту {TURRET_PORT}...")

    while True:
        try:
            data, _ = sock.recvfrom(1024)
            command = data.decode('utf-8')

            with _state_lock:
                if command == "ALLOW":
                    _current_state = "ALLOW_GUEST"
                    logger.warning("[NET] Получена команда: ДОВЕРИТЬ. Турель игнорирует цель.")
                elif command == "FIRE":
                    _current_state = "CHAOS_FIRE"
                    logger.warning("[NET] Получена команда: АТАКОВАТЬ! Включаем периферию.")

        except Exception as e:
            logger.error(f"[NET] Ошибка сокета слушателя: {e}")


def start_turret_listener():
    """Запускает фоновый поток прослушки портов от ТГ-бота"""
    t = threading.Thread(target=_network_worker, daemon=True)
    t.start()


def get_turret_state() -> str:
    """Возвращает текущий режим, прилетевший из Telegram"""
    with _state_lock:
        return _current_state


def send_command_to_turret(command: str):
    """Бот шлет текстовую команду (ALLOW / FIRE) обратно в турель"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(command.encode('utf-8'), (LOCALHOST, TURRET_PORT))
        sock.close()
        logger.warning(f"[NET] Команда {command} отправлена на турель.")
    except Exception as e:
        logger.error(f"[NET] Не удалось отправить команду на турель: {e}")
