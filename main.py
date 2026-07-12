"""Perimeter Security System: <<Smart Turret>>"""

from apps.trainer import show_dataset_dirs, photo_session
from apps.webcam_yolo import turret_vision


if __name__ == '__main__':

    print("\n" + "=" * 60)
    print("HI! This is a perimeter security program. <<Smart Turret>>")
    print("=" * 60)

    while True:
        print("\nSelect one of the items:")

        command = input(
            "1 - Start turret operation. Combat mode, perimeter survey.\n"
            "2 - Train a model. Photo session in front of a webcam.\n"
            "3 - Show list of trusted persons.\n"
            "4 - Exit\n\n"
            "Enter the number: "
        )

        if command == '1':
            print("\n" + "!" * 70)
            print("• The turret can be turned off by pressing the 'Q' key")
            print("• The TG bot is launched as a separate process:  python -m apps.bot_service")
            print("!" * 70 + "\n")
            turret_vision()
        elif command == '2':
            photo_session()
        elif command == '3':
            show_dataset_dirs()
        elif command == '4':
            print("\nProgram shutdown. Bye!")
            break
        else:
            print("\n[ERROR] Command not recognized. Try again.")
