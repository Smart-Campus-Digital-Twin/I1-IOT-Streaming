#include <Wire.h>
#include "Adafruit_SHT31.h"

Adafruit_SHT31 sht30 = Adafruit_SHT31();

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Starting SHT30 test...");

  // ESP32 default I2C pins
  Wire.begin(21, 22);

  // Most SHT30 boards use address 0x44
  if (!sht30.begin(0x44)) {
    Serial.println("SHT30 not found at 0x44. Trying 0x45...");

    if (!sht30.begin(0x45)) {
      Serial.println("SHT30 not found.");
      Serial.println("Check wiring: VCC, GND, SDA=21, SCL=22");
      while (1) {
        delay(10);
      }
    }
  }

  Serial.println("SHT30 found successfully!");
}

void loop() {
  float temperature = sht30.readTemperature();
  float humidity = sht30.readHumidity();

  if (!isnan(temperature)) {
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.println(" °C");
  } else {
    Serial.println("Failed to read temperature.");
  }

  if (!isnan(humidity)) {
    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.println(" %");
  } else {
    Serial.println("Failed to read humidity.");
  }

  Serial.println("--------------------");
  delay(2000);
}
