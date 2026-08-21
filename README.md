# 🤖 Perimeter Security System: "Smart Turret" Core

[ENGLISH VERSION](#en/us) | [РУССКАЯ ВЕРСИЯ](#ru) | [MEDIA](#media)

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
* **Hardware & MCU:** C++ (Arduino Core), ESP32 NodeMCU, ESP32-CAM, Servos MG996R, 5V Relay Trigger

### 📐 System Interface & Architecture
The system features an interactive Console Menu for seamless management and operates using a **Loose Coupling** architecture split into two independent operating system processes communicating via local UDP sockets (`localhost`):

#### 🎛 Console Menu Options (`main.py`):
* **`1` - Start Turret Vision (Combat Mode):** Launches YOLOv8 tracking at a smooth 30 FPS. When an unidentified object is detected, it spins up a background thread (`threading.Thread`) with a thread-safe `Lock` mechanism to compute 128-dimensional facial embedding vectors without freezing the camera stream.
* **`2` - Train Model (Interactive Photo Booth):** Runs an automated enrollment session. It displays live on-screen prompts, takes 5 rapid shots using an OpenCV camera flash effect, normalizes the face matrix, and saves the assets into the database directory under a validated Latin username.
* **`3` - Show Authorized Faces:** Scans the face database structure and prints a clean, organized list of all whitelisted individuals in the console.
* **`4` - Exit:** Cleanly safely releases hardware cameras and shuts down the software core.

#### 📡 Telegram Notification Service (`apps/bot_service.py`):
Acts as the security command center. It listens to inbound network packets on Port 5006, serves interactive image alerts, handles OS file archiving with exact timestamps to prevent disk congestion, and routes control signals (`ALLOW` / `FIRE`) back to the turret on Port 5007.

#### 🎛 Hardware Control & MCU Firmware (`firmware/`):
The physical execution mechanism is managed by an ESP32 micro-controller ecosystem running native C++ firmware, communicate with Python via UDP on Port 8888:
* **`turret_main_esp32/`**: Controls dual high-torque MG996R metal-gear servos for high-speed panning and tilting. It operates a 5V electromagnetic relay (Low Level Trigger) to control a tactical laser unit. 
* **Hardware-Level Bugfix:** To resolve hardware-level logic conflicts between the 3.3V ESP32 GPIO pins and the 5V relay module without physical level shifters, a custom dynamic pin configuration trick was implemented. The MCU swaps modes on-the-fly (`pinMode(INPUT/OUTPUT)`) combined with precise 1.1-second button hold emulations (`delay(1100)`), preventing network UDP buffer overflows caused by servo PWM timer interrupts.
* **`turret_camera_esp32/`**: Manages the independent ESP32-CAM video server. The OV2640 sensor configuration is hardware-locked to crisp HD resolution (`FRAMESIZE_HD` / 1280x720) directly at the EEPROM initialization layer, completely eliminating video stutter and automatic downgrades to VGA mode.
* **Atmospheric UI Feedback:** Integrated a multithreaded `pygame.mixer` audio engine that plays an alert / attack sound upon intruder detection, operating entirely in a non-blocking background OS thread.

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
* **Железо и МК:** C++ (Arduino Core), ESP32 NodeMCU, ESP32-CAM, Сервоприводы MG996R, Реле 5V

### 📐 Интерфейс и архитектура системы
Управление комплексом осуществляется через интерактивное Консольное Меню. Сама система построена на принципах **слабой связанности (Loose Coupling)** и разделена на два независимых процесса ОС, общающихся через сетевой стек оперативной памяти (`localhost`):

#### 🎛 Пункты консольного меню (`main.py`):
* **`1` - Начать работу турели (Боевой режим):** Обрабатывает видеопоток YOLOv8 на стабильных 30 FPS. При обнаружении силуэта запускает фоновый изолированный поток (`threading.Thread`) с механизмом потокобезопасных блокировок (`Lock`). Нейросеть вычисляет отпечаток лица, не вызывая микрофризов основного интерфейса видеокамеры.
* **`2` - Обучить модель (Фотосессия):** Запускает интерактивную регистрацию нового пользователя. Выводит подсказки транслитом на экран, делает 5 быстрых снимков с эффектом вспышки, нормализует матрицу лица и сохраняет кадры в базу данных строго под валидным именем на латинице.
* **`3` - Показать список доверенных лиц:** Сканирует файловую структуру базы данных лиц и выводит в консоль аккуратный список всех авторизованных в системе пользователей.
* **`4` - Выход:** Безопасно освобождает ресурсы видеокамеры и закрывает программу.

#### 📡 Сервис Telegram-уведомлений (`apps/bot_service.py`):
Выступает в роли командного центра охраны. Слушает входящие UDP-пакеты на порту 5006, отправляет интерактивные фото-алерты, автоматически архивирует файлы на диске с фиксацией точного времени (защита от перезаписи) и транслирует обратные приказы пользователя (`ALLOW` / `FIRE`) в сокет турели на порт 5007.

#### 🎛 Аппаратный уровень и прошивка МК (`firmware/`):
Физическое управление механикой возложено на экосистему микроконтроллеров ESP32, работающих на нативном C++ и принимающих команды от Python по UDP-протоколу на порту 8888:
* **`turret_main_esp32/`**: Управляет двумя мощными сервоприводами MG996R с металлическим редуктором для скоростного наведения по осям X и Y. Через 5-вольтовый модуль электромагнитного реле (Low Level Trigger) коммутирует тактический лазерный целеуказатель.
* **Аппаратный хак уровней логики:** Для решения проблемы несовместимости логических уровней (3.3В у GPIO ESP32 против 5В у реле) без использования физических конвертеров, применен алгоритм динамической смены конфигурации пина «на лету» (`pinMode(INPUT/OUTPUT)`). В сочетании с выверенным временем удержания кнопки умного лазера в 1.1 секунды (`delay(1100)`), это полностью исключило забивание сетевого UDP-буфера ШИМ-прерываниями моторов.
* **`turret_camera_esp32/`**: Отвечает за автономный видеосервер ESP32-CAM. Конфигурация матрицы OV2640 жестко зафиксирована на уровне инициализации EEPROM в режиме честного HD (`FRAMESIZE_HD` / 1280x720), что убрало просадки фреймрейта и произвольные сбросы камеры в мыльный VGA-режим.
* **Атмосферное аудио-сопровождение:** Внедрен многопоточный звуковой движок `pygame.mixer`, воспроизводящий сирену / звук атаки при фиксации «Чужого», работающий в изолированном фоновом потоке ОС без микрофризов нейросети.

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
## MEDIA

---

**Screenshots, Photos, Videos**

<div align="center">

<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/screenshots/Auto%20AIM%2003.06.2026%2020_25_34.png" width="360"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/screenshots/Auto%20AIM%2003.06.2026%2020_26_26.png" width="360"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/screenshots/IMG_20260603_202952.jpg" width="360"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/screenshots/IMG_20260810_231252.jpg" width="360"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/photo/IMG_20260808_174415.jpg" width="360"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/photo/IMG_20260813_173017.jpg" width="360"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/photo/IMG_20260813_232644.jpg" width="360"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/photo/IMG_20260819_232352.jpg" width="360"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/photo/IMG_20260819_235427.jpg" width="360"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/photo/IMG_20260819_235447.jpg" width="360"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/photo/IMG_20260820_195428.jpg" width="360"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/photo/IMG_20260820_200350.jpg" width="360"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/photo/IMG_20260820_201004.jpg" width="360"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/photo/IMG_20260820_215302.jpg" width="360"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/screenshots/Auto_AIM_2026-08-20_21-30-04_2.png" width="360"/>
<img src="https://github.com/Demston/ProgramVision_SmartTurret/blob/main/media/screenshots/Auto_AIM_2026-08-20_21-30-04_1.png" width="360"/>

</div>
