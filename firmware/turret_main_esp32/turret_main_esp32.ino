#include <WiFi.h>
#include <WiFiUdp.h>
#include <ESP32Servo.h>

// --- WI-FI SETTINGS---
const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// --- NETWORK SETTINGS ---
WiFiUDP udp;
unsigned int localPort = 8888; // The port specified in Python code
char packetBuffer[255];        // Buffer for incoming packets

// --- PERIPHERAL SETTINGS ---
Servo servoX;  
Servo servoY;  
int pinX = 25;     
int pinY = 26;     
int pinLaser = 27; // Pin for laser relay
bool laser_is_on_now = false;

void setup() {
  Serial.begin(115200);

  // Laser settings (LOW - on, HIGH - off for Low Level relay)
  pinMode(pinLaser, OUTPUT);
  pinMode(pinLaser, HIGH);

  // Allocating PWM channels for servos
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  servoX.setPeriodHertz(50);
  servoY.setPeriodHertz(50);
  servoX.attach(pinX, 500, 2400);
  servoY.attach(pinY, 500, 2400);

  // Connecting to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  
  // Show the board's IP address in the Port Monitor
  Serial.print("ESP32 IP address: ");
  Serial.println(WiFi.localIP());

  // Start listening on a UDP port
  udp.begin(localPort);
  Serial.printf("Listening on UDP port %d\n", localPort);
}

void loop() {
  // 1. Checking if a UDP network packet has arrived from a Python application
  int packetSize = udp.parsePacket();
  
  if (packetSize) {
    // 2. If there is a packet, we read its bytes into the prepared packetBuffer
    int len = udp.read(packetBuffer, 255);
    if (len > 0) packetBuffer[len] = 0; // Put an end-of-line marker
    
    // 3. Converting a byte buffer into a convenient String text object
    String data = String(packetBuffer);
    
    // 4. Look for the positions of semicolons in the format string "X;Y;LASER" (for example, "90;120;1")
    int firstSemi = data.indexOf(';');
    int secondSemi = data.indexOf(';', firstSemi + 1);
    
    // 5. If both semicolons are found, the string is intact and we parse it
    if (firstSemi != -1 && secondSemi != -1) {
      
      // We cut out pieces of text between separators and convert them to integers (toInt)
      int angleX = data.substring(0, firstSemi).toInt();                  // Angle for X motor
      int angleY = data.substring(firstSemi + 1, secondSemi).toInt();     // Angle for Y motor
      int laserOn = data.substring(secondSemi + 1).toInt();               // Laser status (1 or 0)
      
      // 6. Clamp the angles into rigid frames of 0-180 degrees for the safety of mechanics
      angleX = constrain(angleX, 0, 180);
      angleY = constrain(angleY, 0, 180);
      
      // 7. Send physical commands to the PWM channels of the servo drives (the motors rotate)
      servoX.write(angleX);
      servoY.write(angleY);

      // 8. Pulse control for smart laser
      if (laserOn == 1 && !laser_is_on_now) {
        // --- ATTACK MODE: HOLD THE BUTTON FOR ABOUT A SECOND TO TURN ON ---
        pinMode(pinLaser, OUTPUT);
        digitalWrite(pinLaser, LOW);   // We close the relay contacts (press the button)
        delay(1100);                   // Hold for about a second to wake up the laser
        pinMode(pinLaser, INPUT);      // Opened the contacts (released the button)
        
        laser_is_on_now = true;        // REMEMBER: The laser is now ON
      } 
      
      else if (laserOn == 0 && laser_is_on_now) {
        // --- SLEEP MODE: PRESS THE BUTTON FOR ABOUT A SECOND TO TURN OFF ---
        pinMode(pinLaser, OUTPUT);
        digitalWrite(pinLaser, LOW);   // Close the relay contacts again (press the button)
        delay(1100);                   // Hold for about a second to turn off the laser
        pinMode(pinLaser, INPUT);      // Opened the contacts (released the button)
        
        laser_is_on_now = false;       // Now the laser is completely OFF
      }
      
      // 9. We spit out received data into the Port Monitor for visual monitoring
      Serial.printf("Received: X=%d, Y=%d, Laser=%d\n", angleX, angleY, laserOn);
    }
  }
}
