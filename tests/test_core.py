import os
import sys
import socket
import unittest
from dotenv import load_dotenv

# Pass paths so that tests can see modules from the apps and service folders
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from apps.trainer import is_valid_folder_name
from config import DB_PATH, LISTEN_PORT, TURRET_PORT


class TestTurretSoftware(unittest.TestCase):

    def test_valid_folder_names(self):
        """Testing that the regular expression correctly skips normal English names."""
        self.assertTrue(is_valid_folder_name("Dima"))
        self.assertTrue(is_valid_folder_name("Connor"))
        self.assertTrue(is_valid_folder_name("Guest123"))

    def test_invalid_folder_names_cyrillic(self):
        """Testing that the regular expression blocks Cyrillic names."""
        self.assertFalse(is_valid_folder_name("Дима"))
        self.assertFalse(is_valid_folder_name("Гость123"))

    def test_invalid_folder_names_special_chars(self):
        """Testing blocking of prohibited Windows characters and spaces."""
        self.assertFalse(is_valid_folder_name("Dima/Guest"))    # Prohibited sign
        self.assertFalse(is_valid_folder_name("Connor?"))       # Prohibited sign
        self.assertFalse(is_valid_folder_name("Dima Name"))     # Spaces are not allowed
        self.assertFalse(is_valid_folder_name(""))              # Empty line

    def test_dataset_directory_exists(self):
        """Check that the critical dataset folder exists in the root of the project."""
        # The test checks the physical presence of the folder on the disk
        self.assertTrue(os.path.exists(DB_PATH), f"Folder {DB_PATH} not found! Check the deployment.")

    def test_network_ports_are_free(self):
        """Check that ports 5006 and 5007 are free in the system and ready for work."""
        for port in [LISTEN_PORT, TURRET_PORT]:
            with self.subTest(port=port):
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    # Let's try binding the port. If it's busy, an error will pop up.
                    sock.bind(("127.0.0.1", port))
                    port_free = True
                except Exception:
                    port_free = False
                finally:
                    sock.close()

                self.assertTrue(port_free, f"Attention! Port {port} is already taken by another application in Windows")

    def test_env_config_and_token(self):
        """Check that the .env file is in place and the Telegram bot token has loaded."""
        load_dotenv()
        bot_token = os.getenv("BOT_TOKEN")
        self.assertIsNotNone(bot_token, "Critical error: Variable BOT_TOKEN not found in .env file!")
        self.assertNotEqual(bot_token, "", "Error: Bot token in .env file is empty!")


if __name__ == '__main__':
    unittest.main()
