#define IR_A_PIN 32
#define IR_B_PIN 33

#define LED_PIN 2

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(IR_A_PIN, INPUT_PULLUP);
  pinMode(IR_B_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);

  Serial.println("Two IR break-beam sensor test started.");
  Serial.println("Beam clear = HIGH, Beam broken = LOW");
}

void loop() {
  int irA = digitalRead(IR_A_PIN);
  int irB = digitalRead(IR_B_PIN);

  bool irA_broken = (irA == LOW);
  bool irB_broken = (irB == LOW);

  Serial.print("IR A raw: ");
  Serial.print(irA);
  Serial.print(" | IR A broken: ");
  Serial.print(irA_broken);

  Serial.print(" || IR B raw: ");
  Serial.print(irB);
  Serial.print(" | IR B broken: ");
  Serial.println(irB_broken);

  if (irA_broken || irB_broken) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }

  delay(300);
}
