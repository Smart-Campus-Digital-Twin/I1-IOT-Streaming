#define IR_A_PIN 32
#define IR_B_PIN 33
#define LED_PIN 2

#define BEAM_BROKEN_LEVEL LOW

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

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(IR_A_PIN, INPUT_PULLUP);
  pinMode(IR_B_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);

  Serial.println("Occupancy counter started.");
  Serial.println("A then B = Entry");
  Serial.println("B then A = Exit");
}

void loop() {
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
    delay(20);
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
  } else {
    if (millis() - firstBeamTime > SEQUENCE_TIMEOUT) {
      Serial.println("Sequence timeout. Resetting.");
      firstBeam = 0;
    }

    if (firstBeam == 1 && bJustBroken) {
      occupancy++;

      Serial.print("ENTRY detected. Occupancy = ");
      Serial.println(occupancy);

      waitingForClear = true;
    }

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

  delay(20);
}
