import threading
import telebot
from service.bot_handler import network_listener
from service.logger_config import logger, sec_logger
from service.net_bridge import send_command_to_turret
from config import BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)    # Create a bot


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """Handling button clicks in TG"""
    if call.data == "cmd_allow":
        bot.answer_callback_query(call.id, text="Command: Add to trusted")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id,
                                 caption="🚨 Perimeter status: FACILITY AUTHORIZED REMOTELY")
        send_command_to_turret("ALLOW")
        sec_logger.warning("[BOT] TRUST button pressed")

    elif call.data == "cmd_fire":
        bot.answer_callback_query(call.id, text="STROBE AND LASER INCLUDED!")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id,
                                 caption="🚨 Perimeter status: SITE UNDER ATTACK")
        send_command_to_turret("FIRE")
        sec_logger.warning("[BOT] ATTACK button pressed")


if __name__ == "__main__":
    # Launch port listening in a separate background thread (so that it does not interfere with the bot's TG polling)
    net_thread = threading.Thread(target=network_listener, args=(bot,), daemon=True)
    net_thread.start()

    # Launching the TG bot
    logger.info("[BOT] Telegram service has been successfully launched . . .")
    bot.infinity_polling()
