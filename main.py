"""Программа охраны периметра <<Умная Турель>>"""

from apps.trainer import photo_session
from apps.webcam_yolo import turret_vision


if __name__ == '__main__':
    while True:
        print("\n" + "=" * 60)
        print("ПРИВЕТСТВУЮ! Это программа охраны периметра <<Умная Турель>>")
        print("=" * 60)
        print("Выбери один из пунктов:\n")

        command = input(
            "1 - Обучить модель. Фотосессия перед веб-камерой.\n"
            "2 - Начать работу турели. Боевой режим, съёмка периметра.\n"
            "3 - Выход.\n\n"
            "Введи цифру: "
        )

        if command == '1':
            photo_session()
        elif command == '2':
            print("\n" + "!" * 40)
            print("НАПОМИНАНИЕ!")
            print("Выход из камеры осуществляется по кнопке 'Q' (англ. раскладка)")
            print("ТГ-бот запускается отдельным процессом:  python apps/bot_service.py")
            print("!" * 40 + "\n")
            turret_vision()
        elif command == '3':
            print("\nЗавершение работы программы. До связи!")
            break
        else:
            print("\n[ERROR] Команда не распознана. Попробуй еще раз.")
