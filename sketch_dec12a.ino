#include <Keypad.h>
#include <Stepper.h>
const byte ROWS = 4; //four rows
const byte COLS = 4; //four columns

char keys[ROWS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};
const int stepsPerRevolution = 800;

Stepper mystepper(stepsPerRevolution, A1, A2, A2, A4);

byte rowPins[ROWS] = {9, 8, 7, 6};
byte colPins[COLS] = {5, 4, 3, 2}; 
Keypad keypad = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS );

const int ledPin =  3;

void setup(){
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);
  mystepper.setSpeed(35);
  Serial.begin(9600);
}

bool set = false;
int rcv = 0;
int del = 100;

void loop(){
  int i = 0;
  del = 200;
  // LED
  unsigned long currentMillis = millis();
  if (set == true) {
    digitalWrite(ledPin, HIGH);
    delay(del);
    digitalWrite(ledPin, LOW);
    delay(del);
  }
  // read
   if (Serial.available() > 0) {
      rcv = Serial.read();
      if (rcv == '2') {
        set = true;
        }
  }
  char key = keypad.getKey();// Read the key
  if (key == '1' && set == true) {
    Serial.println("1");
    while( i < 4) {
      mystepper.step(stepsPerRevolution);
      i += 1;
    }
    set = false;
    }
}
