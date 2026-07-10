import sys
import os

# Pass paths so that tests can see modules from the apps and service folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from config import ESP_IP, ESP_PORT
from service.net_bridge import send_angles_to_esp


def main():
    print("[TEST] The manual turret control panel has been launched!")
    print("Enter angles from 0 to 180, separated by spaces. Format: X Y LASER")
    print("Example: '90 90 1' (Center, Laser ON) or '45 135 0' (Laser OFF)")
    print("To exit, enter 'exit'\n")

    # Initially, we place the turret in the central position
    current_x = 90
    current_y = 90
    send_angles_to_esp(current_x, current_y, 0)

    while True:
        try:
            user_input = input("Enter the command(X Y LASER): ").strip()

            if user_input.lower() == 'exit':
                print("Turn off the remote control...")
                break

            # Парсим ввод пользователя
            parts = user_input.split()
            if len(parts) != 3:
                print("❌ Error! You must enter exactly 3 digits separated by spaces.")
                continue

            x = int(parts[0])
            y = int(parts[1])
            laser = int(parts[2])

            print(f"🚀 Send to the ESP32: X={x}°, Y={y}°, Laser={laser}")
            send_angles_to_esp(x, y, laser)

        except ValueError:
            print("❌ Error! Enter only integers.")
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
