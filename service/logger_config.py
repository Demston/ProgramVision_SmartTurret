import logging
import os
from config import LOGS_DIR, SYSTEM_LOG, SECURITY_LOG

os.makedirs(LOGS_DIR, exist_ok=True)


def setup_logger():
    """Setting up custom logging for a project."""

    # Basic format for outputting log lines (Time [Level] Message)
    log_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # The main root logger of the system
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Clear old handlers so that logs are not duplicated during a restart
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Handler А: Outputting logs to the console instead of the standard print()
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

    # Handler Б: Recording ERRORS and program notifications in the system_runtime.log
    system_file_handler = logging.FileHandler(SYSTEM_LOG, encoding='utf-8')
    system_file_handler.setFormatter(log_format)
    system_file_handler.setLevel(logging.INFO)
    root_logger.addHandler(system_file_handler)

    # Creating a SEPARATE independent logger just for security alerts
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)
    security_logger.propagate = False  # To prevent security alerts from being duplicated in system_runtime

    # Handler В: Record only ALARMS and alerts in security_alerts.log
    security_file_handler = logging.FileHandler(SECURITY_LOG, encoding='utf-8')
    security_file_handler.setFormatter(log_format)
    security_logger.addHandler(security_file_handler)

    # Adding alert output to the console, so you can see them on your screen.
    security_logger.addHandler(console_handler)


# Initialize when importing the module
setup_logger()

# Exporting ready-made loggers for use in code
logger = logging.getLogger("root")  # For errors, network notifications, system statuses
sec_logger = logging.getLogger("security")  # Strictly for the purpose of recording OWNER/UNKNOWN violators
