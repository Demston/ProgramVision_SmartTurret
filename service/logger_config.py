import logging
import os
from config import *

os.makedirs(LOGS_DIR, exist_ok=True)


def setup_logger():
    """Настройка кастомного логирования для проекта"""

    # Базовый формат для вывода строк лога (Время [Уровень] Сообщение)
    log_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Главный корневой логгер системы
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Очищаем старые хэндлеры, чтобы логи не дублировались при перезапуске
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Handler А: Вывод логов в консоль вместо стандартных print()
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

    # Handler Б: Запись ОШИБОК и уведомлений работы программы в system_runtime.log
    system_file_handler = logging.FileHandler(SYSTEM_LOG, encoding='utf-8')
    system_file_handler.setFormatter(log_format)
    system_file_handler.setLevel(logging.INFO)
    root_logger.addHandler(system_file_handler)

    # 3. Создаем ОТДЕЛЬНЫЙ независимый логгер только для алертов безопасности
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)
    security_logger.propagate = False  # Чтобы алерты безопасности не дублировались в system_runtime

    # Handler В: Запись только ТРЕВОГ и алертов в security_alerts.log
    security_file_handler = logging.FileHandler(SECURITY_LOG, encoding='utf-8')
    security_file_handler.setFormatter(log_format)
    security_logger.addHandler(security_file_handler)

    # Добавляем вывод алертов в консоль, чтобы ты видел их на экране
    security_logger.addHandler(console_handler)


# Инициализируем при импорте модуля
setup_logger()

# Экспортируем готовые логгеры для использования в коде
logger = logging.getLogger("root")  # Для ошибок, сетевых уведомлений, системных статусов
sec_logger = logging.getLogger("security")  # Строго для фиксации OWNER / UNKNOWN нарушителей
