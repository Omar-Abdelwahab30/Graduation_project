const int speedPin = 5;  // PWM pin connected to the motor driver
const int scPin = 2;  // Pin connected to the SC signal (replace with the actual pin)
volatile unsigned long pulseCount = 0;
unsigned long lastUpdateTime = 0;
const int pulsesPerRevolution = 20;  // Replace with the actual value from your motor datasheet
int speedValue = 0;  // Variable to store the speed value

void setup() {
  Serial.begin(9600);
  pinMode(speedPin, OUTPUT);
  pinMode(scPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(scPin), countPulse, RISING);  // Adjust interrupt mode if needed
  lastUpdateTime = millis();
}

void loop() {
  unsigned long currentTime = millis();
  if (currentTime - lastUpdateTime >= 1000) {  // Update RPM every second
    detachInterrupt(digitalPinToInterrupt(scPin));  // Temporarily disable interrupts
    unsigned long rpm = (60 * pulseCount) / (pulsesPerRevolution * (currentTime - lastUpdateTime) / 1000.0);
    Serial.print("RPM: ");
    Serial.println(rpm);
    pulseCount = 0;
    lastUpdateTime = currentTime;
    attachInterrupt(digitalPinToInterrupt(scPin), countPulse, RISING);  // Re-enable interrupts
  }

  if (Serial.available() > 0) {  // Check for speed control input
    speedValue = Serial.parseInt();
    if (speedValue >= 0 && speedValue <= 255) {
      analogWrite(speedPin, speedValue);
      Serial.print("Speed set to: ");
      Serial.println(speedValue);
    } else {
      Serial.println("Please enter a value between 0 and 255.");
    }
    while (Serial.available() > 0) {  // Clear serial buffer
      Serial.read();
    }
  }
}

void countPulse() {
  pulseCount++;
}
