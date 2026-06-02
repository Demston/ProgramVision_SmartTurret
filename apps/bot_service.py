import threading
import telebot
from service.bot_handler import *
from service.logger_config import logger, sec_logger


bot = telebot.TeleBot(BOT_TOKEN)    # Создаем бота


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """Обработка нажатия кнопок в ТГ"""
    if call.data == "cmd_allow":
        bot.answer_callback_query(call.id, text="Команда: Добавить в доверенные")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id,
                                 caption="🚨 Статус периметра: ОБЪЕКТ АВТОРИЗОВАН УДАЛЕННО")
        send_command_to_turret("ALLOW")
        sec_logger.warning("[BOT] Нажата кнопка ДОВЕРИТЬ")

    elif call.data == "cmd_fire":
        bot.answer_callback_query(call.id, text="ВКЛЮЧЕН СТРОБОСКОП И ЛАЗЕР!")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.id,
                                 caption="🚨 Статус периметра: ОБЪЕКТ АТАКОВАН")
        send_command_to_turret("FIRE")
        sec_logger.warning("[BOT] Нажата кнопка АТАКА")


if __name__ == "__main__":
    # Запускаем прослушку портов в отдельном фоновом потоке (чтобы она не мешала боту опрашивать ТГ)
    net_thread = threading.Thread(target=network_listener(bot), daemon=True)
    net_thread.start()

    # Запуск самого ТГ бота
    logger.info("[BOT] Telegram-сервис успешно запущен . . .")
    bot.infinity_polling()
