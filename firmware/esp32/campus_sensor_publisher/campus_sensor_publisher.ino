#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include "Adafruit_SHT31.h"

// -------------------- WiFi Details --------------------
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// -------------------- MQTT Details --------------------
const char* MQTT_BROKER = "broker.hivemq.com";
const int MQTT_PORT = 1883;

const char* MQTT_TOPIC = "smartclassroom/classroom001/telemetry";

// -------------------- SHT30 --------------------
Adafruit_SHT31 sht30 = Adafruit_SHT31();

#define SDA_PIN 21
#define SCL_PIN 22

// -------------------- IR Sensors --------------------
#define IR_A_PIN 32
#define IR_B_PIN 33
#define LED_PIN 2

// Your IR sensors:
// Beam clear  = HIGH
// Beam broken = LOW
#define BEAM_BROKEN_LEVEL LOW

// -------------------- MQTT Objects --------------------
WiFiClient espClient;
PubSubClient mqtt(espClient);

// -------------------- Occupancy Variables --------------------
int occupancy = 0;

bool prevA = false;
bool prevB = false;

int firstBeam = 0;
// 0 = none
// 1 = IR A first
// 2 = IR B first

unsigned long firstBeamTime = 0;
const unsigned long SEQUENCE_TIMEOUT = 4000;

bool waitingForClear = false;

// -------------------- Temperature Variables --------------------
float temperature = 0.0;

// -------------------- Timing --------------------
unsigned long lastTempReadTime = 0;
const unsigned long TEMP_READ_INTERVAL = 2000;

unsigned long lastMqttPublishTime = 0;
const unsigned long MQTT_PUBLISH_INTERVAL = 5000;

// -------------------- WiFi Connect --------------------
void connectWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected.");
  Serial.print("ESP32 IP address: ");
  Serial.println(WiFi.localIP());
}

// -------------------- MQTT Connect --------------------
void connectMQTT() {
  while (!mqtt.connected()) {
    Serial.println("Connecting to MQTT...");

    String clientId = "ESP32-Classroom001-";
    clientId += String((uint32_t)ESP.getEfuseMac(), HEX);

    if (mqtt.connect(clientId.c_str())) {
      Serial.println("MQTT connected.");
    } else {
      Serial.print("MQTT failed. State: ");
      Serial.println(mqtt.state());
      Serial.println("Trying again in 2 seconds...");
      delay(2000);
    }
  }
}

// -------------------- Read Temperature --------------------
void readTemperature() {
  float t = sht30.readTemperature();

  if (!isnan(t)) {
    temperature = t;
  } else {
    Serial.println("Warning: Failed to read SHT30 temperature.");
  }
}

// -------------------- Publish MQTT --------------------
void publishMQTT() {
  char payload[160];

  snprintf(payload, sizeof(payload),
           "{\"classroom\":\"classroom001\",\"temperature_c\":%.2f,\"occupancy_count\":%d}",
           temperature,
           occupancy);

  bool success = mqtt.publish(MQTT_TOPIC, payload);

  if (success) {
    Serial.print("MQTT published: ");
    Serial.println(payload);
  } else {
    Serial.println("MQTT publish failed.");
  }
}

// -------------------- Update Occupancy --------------------
void updateOccupancy() {
  bool currentA = digitalRead(IR_A_PIN) == BEAM_BROKEN_LEVEL;
  bool currentB = digitalRead(IR_B_PIN) == BEAM_BROKEN_LEVEL;

  bool aJustBroken = currentA && !prevA;
  bool bJustBroken = currentB && !prevB;

  if (currentA || currentB) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }

  if (waitingForClear) {
    if (!currentA && !currentB) {
      waitingForClear = false;
      firstBeam = 0;
      Serial.println("Both beams clear. Ready for next person.");
    }

    prevA = currentA;
    prevB = currentB;
    return;
  }

  if (firstBeam == 0) {
    if (aJustBroken) {
      firstBeam = 1;
      firstBeamTime = millis();
      Serial.println("IR A broken first");
    } 
    else if (bJustBroken) {
      firstBeam = 2;
      firstBeamTime = millis();
      Serial.println("IR B broken first");
    }
  } 
  else {
    if (millis() - firstBeamTime > SEQUENCE_TIMEOUT) {
      Serial.println("Sequence timeout. Resetting.");
      firstBeam = 0;
    }

    // A then B = Entry
    if (firstBeam == 1 && bJustBroken) {
      occupancy++;

      Serial.print("ENTRY detected. Occupancy = ");
      Serial.println(occupancy);

      waitingForClear = true;

      // Send MQTT immediately when occupancy changes
      publishMQTT();
    }

    // B then A = Exit
    if (firstBeam == 2 && aJustBroken) {
      if (occupancy > 0) {
        occupancy--;
      }

      Serial.print("EXIT detected. Occupancy = ");
      Serial.println(occupancy);

      waitingForClear = true;

      // Send MQTT immediately when occupancy changes
      publishMQTT();
    }
  }

  prevA = currentA;
  prevB = currentB;
}

// -------------------- Setup --------------------
void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(IR_A_PIN, INPUT_PULLUP);
  pinMode(IR_B_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);

  Wire.begin(SDA_PIN, SCL_PIN);

  Serial.println("Starting Smart Classroom MQTT prototype...");

  if (!sht30.begin(0x44)) {
    Serial.println("SHT30 not found at 0x44. Trying 0x45...");

    if (!sht30.begin(0x45)) {
      Serial.println("SHT30 not found.");
      Serial.println("Check wiring: VIN, GND, SDA/RH=21, SCL/T=22");
      while (1) {
        delay(10);
      }
    }
  }

  Serial.println("SHT30 found successfully.");

  readTemperature();

  connectWiFi();

  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  connectMQTT();

  Serial.println("System ready.");
  Serial.println("Publishing only temperature and occupancy count.");
}

// -------------------- Main Loop --------------------
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  if (!mqtt.connected()) {
    connectMQTT();
  }

  mqtt.loop();

  // IR occupancy must run continuously
  updateOccupancy();

  // Read temperature every 2 seconds
  if (millis() - lastTempReadTime >= TEMP_READ_INTERVAL) {
    lastTempReadTime = millis();
    readTemperature();
  }

  // Publish normal telemetry every 5 seconds
  if (millis() - lastMqttPublishTime >= MQTT_PUBLISH_INTERVAL) {
    lastMqttPublishTime = millis();
    publishMQTT();
  }

  delay(20);
}
