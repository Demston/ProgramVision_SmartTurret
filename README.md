# 🤖 Perimeter Security System: "Smart Turret" Core

[ENGLISH VERSION](#en/us) | [РУССКАЯ ВЕРСИЯ](#ru)

---

## [EN/US]

An asynchronous, distributed AI-powered security complex that locks onto human targets, performs biometric authentication in a background thread, and provides real-time remote control via an interactive Telegram Bot. Equipped with a unified console menu interface and infrastructure auto-tests.

### 🛠 Tech Stack
* **Core Logic:** Python 3.10+ (Object-Oriented, Multithreaded, Event-Driven)
* **Computer Vision & AI:** Ultralytics YOLOv8 (Target Detection & Tracking), DeepFace (VGG-Face Architecture)
* **Networking & IPC:** Low-level UDP Sockets (Asynchronous Two-Way Network Bridge)
* **Remote Control:** pyTelegramBotAPI (`telebot` with Inline Keyboards)
* **Quality Assurance:** `unittest` framework (Infrastructure, validation, and network port tests)
* **Logging:** Native `logging` system (Splitting system runtime and security breach logs)

### 📐 System Interface & Architecture
The system features an interactive Console Menu for seamless management and operates using a **Loose Coupling** architecture split into two independent operating system processes communicating via local UDP sockets (`localhost`):

#### 🎛 Console Menu Options (`main.py`):
* **`1` - Start Turret Vision (Combat Mode):** Launches YOLOv8 tracking at a smooth 30 FPS. When an unidentified object is detected, it spins up a background thread (`threading.Thread`) with a thread-safe `Lock` mechanism to compute 128-dimensional facial embedding vectors without freezing the camera stream.
* **`2` - Train Model (Interactive Photo Booth):** Runs an automated enrollment session. It displays live on-screen prompts, takes 5 rapid shots using an OpenCV camera flash effect, normalizes the face matrix, and saves the assets into the database directory under a validated Latin username.
* **`3` - Show Authorized Faces:** Scans the face database structure and prints a clean, organized list of all whitelisted individuals in the console.
* **`4` - Exit:** Cleanly safely releases hardware cameras and shuts down the software core.

#### 📡 Telegram Notification Service (`apps/bot_service.py`):
Acts as the security command center. It listens to inbound network packets on Port 5006, serves interactive image alerts, handles OS file archiving with exact timestamps to prevent disk congestion, and routes control signals (`ALLOW` / `FIRE`) back to the turret on Port 5007.

### 🚀 Getting Started

1. **Clone & Setup Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables (`.env`):**
   Create a `.env` file in the root directory:
   ```env
   BOT_TOKEN=your_telegram_bot_token
   MY_CHAT_ID=your_personal_telegram_chat_id
   ```

3. **Run Infrastructure Tests:**
   Ensure network ports `5006`/`5007` are free, `.env` variables are active, and paths are valid:
   ```bash
   python -m unittest tests/test_core.py
   ```

4. **Execution:**
   * **Terminal 1** (Start the Telegram Control Center process):
     ```bash
     python apps/bot_service.py
     ```
   * **Terminal 2** (Start the Main Console Interface complex):
     ```bash
     python main.py
     ```

---

## [RU]

Асинхронный распределенный охранный комплекс на базе искусственного интеллекта. Система автоматически захватывает цели, проводит биометрическую верификацию лиц в фоновом потоке и предоставляет интерфейс удаленного управления через интерактивного Telegram-бота. Снабжена удобным консольным меню и автотестами инфраструктуры.

### 🛠 Технологический стек
* **Ядро системы:** Python 3.10+ (ООП, Многопоточность, Событийно-ориентированная логика)
* **Нейросети и CV:** Ultralytics YOLOv8 (Детекция и трекинг силуэтов), DeepFace (Архитектура VGG-Face)
* **Сетевой уровень (IPC):** Низкоуровневые сокеты UDP (Двусторонний асинхронный сетевой шлюз)
* **Удаленное управление:** pyTelegramBotAPI (`telebot` с Inline-клавиатурами)
* **Тестирование:** Фреймворк `unittest` (Автотесты сетевой инфраструктуры, валидации и путей)
* **Логирование:** Встроенный модуль `logging` (Разделение потоков системных логов и тревог безопасности)

### 📐 Интерфейс и архитектура системы
Управление комплексом осуществляется через интерактивное Консольное Меню. Сама система построена на принципах **слабой связанности (Loose Coupling)** и разделена на два независимых процесса ОС, общающихся через сетевой стек оперативной памяти (`localhost`):

#### 🎛 Пункты консольного меню (`main.py`):
* **`1` - Начать работу турели (Боевой режим):** Обрабатывает видеопоток YOLOv8 на стабильных 30 FPS. При обнаружении силуэта запускает фоновый изолированный поток (`threading.Thread`) с механизмом потокобезопасных блокировок (`Lock`). Нейросеть вычисляет отпечаток лица, не вызывая микрофризов основного интерфейса видеокамеры.
* **`2` - Обучить модель (Фотосессия):** Запускает интерактивную регистрацию нового пользователя. Выводит подсказки транслитом на экран, делает 5 быстрых снимков с эффектом вспышки, нормализует матрицу лица и сохраняет кадры в базу данных строго под валидным именем на латинице.
* **`3` - Показать список доверенных лиц:** Сканирует файловую структуру базы данных лиц и выводит в консоль аккуратный список всех авторизованных в системе пользователей.
* **`4` - Выход:** Безопасно освобождает ресурсы видеокамеры и закрывает программу.

#### 📡 Сервис Telegram-уведомлений (`apps/bot_service.py`):
Выступает в роли командного центра охраны. Слушает входящие UDP-пакеты на порту 5006, отправляет интерактивные фото-алерты, автоматически архивирует файлы на диске с фиксацией точного времени (защита от перезаписи) и транслирует обратные приказы пользователя (`ALLOW` / `FIRE`) в сокет турели на порт 5007.

### 🚀 Быстрый запуск

1. **Развертывание окружения:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Для Linux/MacOS: source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Настройка переменных окружения (`.env`):**
   Создайте файл `.env` в корневом каталоге проекта:
   ```env
   BOT_TOKEN=токен_вашего_телеграм_бота
   MY_CHAT_ID=ваш_личный_chat_id_в_телеграм
   ```

3. **Прогон тестов инфраструктуры:**
   Проверьте готовность портов `5006`/`5007`, наличие `.env` и валидность путей к базам данных:
   ```bash
   python tests/test_core.py
   ```

4. **Запуск комплекса:**
   * **Окно терминала 1** (Включение центра уведомлений бота):
     ```bash
     python apps/bot_service.py
     ```
   * **Окно терминала 2** (Включение главного пульта управления через меню):
     ```bash
     python main.py
     ```

---

<div align="center">
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/screenshots/Auto%20AIM%2003.06.2026%2020_25_34.png" width="480"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/screenshots/Auto%20AIM%2003.06.2026%2020_26_20.png" width="480"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/screenshots/IMG_20260603_202952.jpg" width="320"/>
</div>
