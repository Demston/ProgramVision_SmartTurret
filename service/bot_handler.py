import os
import socket
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from service.logger_config import logger, sec_logger
from config import LOCALHOST, LISTEN_PORT, ALERTS_DIR, ALERT_IMG_PATH, CHAT_ID


def network_listener(our_bot):
    """Runs in the background. Listens on port 5006."""
    logger.info(f"[BOT NET] The network bridge is running. Listening on port {LISTEN_PORT}...")

    bot = our_bot
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", LISTEN_PORT))  # LOCALHOST

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            signal = data.decode('utf-8')

            if signal == "NEW_ALERT":
                logger.error("[BOT NET] Turret alert received! Sending photo of intruder...")
                send_security_alert(bot)
        except Exception as e:
            logger.error(f"[BOT NET] Critical failure: {e}")


def send_security_alert(bot):
    """Sending photos and buttons to Telegram"""
    try:
        if os.path.exists(ALERT_IMG_PATH):
            with open(ALERT_IMG_PATH, 'rb') as f:
                photo = f.read()  # The file has been read and is no longer occupied by Windows
            # Create interactive buttons under photos
            markup = InlineKeyboardMarkup()
            btn_allow = InlineKeyboardButton("🟢 TRUST", callback_data="cmd_allow")
            btn_fire = InlineKeyboardButton("🔴 ATTACK", callback_data="cmd_fire")
            markup.row(btn_allow, btn_fire)

            bot.send_photo(
                CHAT_ID,
                photo,
                caption="🚨 ATTENTION! Unidentified perimeter object detected!",
                reply_markup=markup
            )
            logger.info("[BOT] The photo has been successfully sent to Telegram.")

            # Form an archive name based on date and time
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_filename = f"alert_{timestamp}.jpg"
            archive_path = os.path.join(ALERTS_DIR, archive_filename)  # Full path to the archive photo
            os.rename(ALERT_IMG_PATH, archive_path)         # Renaming a temporary file to an archive file
            logger.info(f"[BOT] The file has been moved to the archive: {archive_path}")
        else:
            logger.error(f"[BOT] File {ALERT_IMG_PATH} not found on disk!")
    except Exception as e:
        logger.error(f"[BOT] Failed to send message to Telegram: {e}")
