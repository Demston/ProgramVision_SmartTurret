"""Программа охраны периметра <<Умная Турель>>"""

from apps.trainer import show_dataset_dirs, photo_session
from apps.webcam_yolo import turret_vision


if __name__ == '__main__':

    print("\n" + "=" * 60)
    print("ПРИВЕТСТВУЮ! Это программа охраны периметра <<Умная Турель>>")
    print("=" * 60)

    while True:
        print("\nВыбери один из пунктов:")

        command = input(
            "1 - Начать работу турели. Боевой режим, съёмка периметра.\n"
            "2 - Обучить модель. Фотосессия перед веб-камерой.\n"
            "3 - Показать список доверенных лиц.\n"
            "4 - Выход.\n\n"
            "Введи цифру: "
        )

        if command == '1':
            print("\n" + "!" * 70)
            print("• Выключение турели осуществляется по кнопке 'Q' (англ. раскладка)")
            print("• ТГ-бот запускается отдельным процессом:  python apps/bot_service.py")
            print("!" * 70 + "\n")
            turret_vision()
        elif command == '2':
            photo_session()
        elif command == '3':
            show_dataset_dirs()
        elif command == '4':
            print("\nЗавершение работы программы. До связи!")
            break
        else:
            print("\n[ERROR] Команда не распознана. Попробуй еще раз.")
