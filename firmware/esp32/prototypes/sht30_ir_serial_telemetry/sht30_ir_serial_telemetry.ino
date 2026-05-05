#include <Wire.h>
#include "Adafruit_SHT31.h"

// -------------------- SHT30 --------------------
Adafruit_SHT31 sht30 = Adafruit_SHT31();

#define SDA_PIN 21
#define SCL_PIN 22

// -------------------- IR Sensors --------------------
#define IR_A_PIN 32
#define IR_B_PIN 33
#define LED_PIN 2

// Your IR sensor result:
// Beam clear  = HIGH
// Beam broken = LOW
#define BEAM_BROKEN_LEVEL LOW

// -------------------- Occupancy Variables --------------------
int occupancy = 0;

bool prevA = false;
bool prevB = false;

int firstBeam = 0;
// 0 = no beam first
// 1 = IR A first
// 2 = IR B first

unsigned long firstBeamTime = 0;
const unsigned long SEQUENCE_TIMEOUT = 4000;

bool waitingForClear = false;

// -------------------- Temperature Timing --------------------
unsigned long lastTempReadTime = 0;
const unsigned long TEMP_READ_INTERVAL = 2000;

float temperature = 0.0;
float humidity = 0.0;

// -------------------- Telemetry Print Timing --------------------
unsigned long lastPrintTime = 0;
const unsigned long PRINT_INTERVAL = 1000;

// -------------------- Function: Read SHT30 --------------------
void readSHT30() {
  float t = sht30.readTemperature();
  float h = sht30.readHumidity();

  if (!isnan(t) && !isnan(h)) {
    temperature = t;
    humidity = h;
  } else {
    Serial.println("Warning: Failed to read SHT30.");
  }
}

// -------------------- Function: Update Occupancy --------------------
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

  // After one count, wait until both beams are clear
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

  // Detect which beam was broken first
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
  } else {
    // Reset if person does not complete crossing
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
    }

    // B then A = Exit
    if (firstBeam == 2 && aJustBroken) {
      if (occupancy > 0) {
        occupancy--;
      }

      Serial.print("EXIT detected. Occupancy = ");
      Serial.println(occupancy);

      waitingForClear = true;
    }
  }

  prevA = currentA;
  prevB = currentB;
}

// -------------------- Function: Print Current Data --------------------
void printTelemetry() {
  bool irA_broken = digitalRead(IR_A_PIN) == BEAM_BROKEN_LEVEL;
  bool irB_broken = digitalRead(IR_B_PIN) == BEAM_BROKEN_LEVEL;

  Serial.println("---------- SENSOR STATUS ----------");

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" C");

  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");

  Serial.print("IR A broken: ");
  Serial.println(irA_broken ? "YES" : "NO");

  Serial.print("IR B broken: ");
  Serial.println(irB_broken ? "YES" : "NO");

  Serial.print("Occupancy: ");
  Serial.println(occupancy);

  Serial.println("-----------------------------------");
}

// -------------------- Setup --------------------
void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(IR_A_PIN, INPUT_PULLUP);
  pinMode(IR_B_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);

  Wire.begin(SDA_PIN, SCL_PIN);

  Serial.println("Starting combined SHT30 + IR sensor test...");

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

  Serial.println("SHT30 found successfully!");
  Serial.println("IR logic: Beam clear = HIGH, Beam broken = LOW");
  Serial.println("A then B = Entry");
  Serial.println("B then A = Exit");

  readSHT30();
}

// -------------------- Main Loop --------------------
void loop() {
  // Read IR sensors continuously
  updateOccupancy();

  // Read temperature/humidity every 2 seconds
  if (millis() - lastTempReadTime >= TEMP_READ_INTERVAL) {
    lastTempReadTime = millis();
    readSHT30();
  }

  // Print full sensor status every 1 second
  if (millis() - lastPrintTime >= PRINT_INTERVAL) {
    lastPrintTime = millis();
    printTelemetry();
  }

  delay(20);
}
