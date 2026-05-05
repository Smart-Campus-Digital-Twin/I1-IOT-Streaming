#include <Wire.h>

void scanBus(int sdaPin, int sclPin) {
  Wire.end();
  delay(200);

  pinMode(sdaPin, INPUT_PULLUP);
  pinMode(sclPin, INPUT_PULLUP);

  Wire.begin(sdaPin, sclPin);
  Wire.setClock(50000); // slower I2C for easier detection

  delay(200);

  Serial.print("Scanning with SDA = GPIO ");
  Serial.print(sdaPin);
  Serial.print(", SCL = GPIO ");
  Serial.println(sclPin);

  int deviceCount = 0;

  for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    byte error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("I2C device found at address 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
      deviceCount++;
    }
  }

  if (deviceCount == 0) {
    Serial.println("No I2C devices found.");
  } else {
    Serial.print("Total devices found: ");
    Serial.println(deviceCount);
  }

  Serial.println("----------------------");
}

void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println();
  Serial.println("ESP32 I2C scanner started.");
}

void loop() {
  // Normal ESP32 I2C wiring
  scanBus(21, 22);

  // Swapped test
  scanBus(22, 21);

  delay(4000);
}
