#define IR_PIN 32
#define LED_PIN 2

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(IR_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);

  Serial.println("IR break-beam sensor test started.");
  Serial.println("Break and unblock the beam.");
}

void loop() {
  int sensorValue = digitalRead(IR_PIN);

  Serial.print("IR raw value: ");
  Serial.print(sensorValue);

  if (sensorValue == LOW) {
    Serial.println("  -> LOW");
    digitalWrite(LED_PIN, HIGH);
  } else {
    Serial.println("  -> HIGH");
    digitalWrite(LED_PIN, LOW);
  }

  delay(300);
}
