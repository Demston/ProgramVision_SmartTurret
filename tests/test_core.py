import os
import sys
import socket
import unittest
from dotenv import load_dotenv

# Прокидываем пути, чтобы тесты видели модули из папки apps и service
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from apps.trainer import is_valid_folder_name
from config import DB_PATH, LISTEN_PORT, TURRET_PORT


class TestTurretSoftware(unittest.TestCase):

    def test_valid_folder_names(self):
        """Тестируем, что регулярка правильно пропускает нормальные английские имена"""
        self.assertTrue(is_valid_folder_name("Dima"))
        self.assertTrue(is_valid_folder_name("Connor"))
        self.assertTrue(is_valid_folder_name("Guest123"))

    def test_invalid_folder_names_cyrillic(self):
        """Тестируем, что регулярка блокирует кириллическое имя"""
        self.assertFalse(is_valid_folder_name("Дима"))
        self.assertFalse(is_valid_folder_name("Гость123"))

    def test_invalid_folder_names_special_chars(self):
        """Тестируем блокировку запрещенных символов Windows и пробелов"""
        self.assertFalse(is_valid_folder_name("Dima/Guest"))  # Знак запрещен
        self.assertFalse(is_valid_folder_name("Connor?"))  # Знак запрещен
        self.assertFalse(is_valid_folder_name("Dima Name"))  # Пробел запрещен
        self.assertFalse(is_valid_folder_name(""))  # Пустая строка

    def test_dataset_directory_exists(self):
        """Проверяем, что критически важная папка dataset существует в корне проекта"""
        # Тест проверяет физическое наличие папки на диске F:
        self.assertTrue(os.path.exists(DB_PATH), f"Папка {DB_PATH} не найдена! Проверь деплой.")

    def test_network_ports_are_free(self):
        """Проверяем, что порты 5006 и 5007 свободны в системе и готовы к работе"""
        for port in [LISTEN_PORT, TURRET_PORT]:
            with self.subTest(port=port):
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    # Пробуем забиндить порт. Если он занят — вылетит ошибка
                    sock.bind(("127.0.0.1", port))
                    port_free = True
                except Exception:
                    port_free = False
                finally:
                    sock.close()

                self.assertTrue(port_free, f"Внимание! Порт {port} уже занят другим приложением в Windows!")

    def test_env_config_and_token(self):
        """Проверяем, что файл .env на месте, а токен Telegram-бота подгрузился"""
        load_dotenv()  # Подгружаем .env
        bot_token = os.getenv("BOT_TOKEN")
        self.assertIsNotNone(bot_token, "Критическая ошибка: Переменная BOT_TOKEN не найдена в файле .env!")
        self.assertNotEqual(bot_token, "", "Ошибка: Токен бота в .env файле пустой!")


if __name__ == '__main__':
    unittest.main()
