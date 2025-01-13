#include <Arduino.h>
#include "AccelStepper.h"

#include "MotorVID28.h"
#include "util.h"
#include <Wire.h>

#include "pins_arduino.h"

#define USE_MICROSTEPS 1
#define MONITOR_PIN 12

#define MOTOR_ROW 2
#define MOTOR_COL 5

#if USE_MICROSTEPS
bool microstepMode = true;
#define STEPS_PER_STEP (MOTORVID28_NUM_MICROSTEPS / 6)
#else
bool microstepMode = false;
#define STEPS_PER_STEP (1)
#endif


#define DEGREES_TO_STEPS(x)  (3*x * STEPS_PER_STEP)
#define NUM_STEPS (DEGREES_TO_STEPS(360))

#define HAND_SPEED (2.0 * STEPS_PER_STEP)
#define HAND_ACCELERATION (0.03 * STEPS_PER_STEP)

MotorVID28 motor0(NUM_STEPS, microstepMode, 5, 3, 6);
MotorVID28 motor1(NUM_STEPS, microstepMode, 10, 9, 11);

void stepper0_fw() { 
  motor0.stepUp(); 
  digitalWrite(MONITOR_PIN, motor0.currentStep & 0x1); 
}
void stepper0_bw() { 
  motor0.stepDown(); 
  digitalWrite(MONITOR_PIN, motor1.currentStep & 0x1);
}

void stepper1_fw() { motor1.stepUp(); }
void stepper1_bw() { motor1.stepDown(); }

AccelStepper stepper0(stepper0_bw, stepper0_fw);
AccelStepper stepper1(stepper1_bw, stepper1_fw);

#define TOTAL_NUM_MOTORS 48
int16_t inputTargets[TOTAL_NUM_MOTORS]; //extra sync bytes at end
bool new_targets = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.print("Nano started for motor [");
  Serial.print(MOTOR_ROW);
  Serial.print(" , ");
  Serial.print(MOTOR_COL);
  Serial.println("]");

  stepper0.setMaxSpeed(HAND_SPEED);
  stepper0.setAcceleration(HAND_ACCELERATION);

  stepper1.setMaxSpeed(HAND_SPEED);
  stepper1.setAcceleration(HAND_ACCELERATION);
  
  int divisor = 1;
  setPrescaler(0, divisor);
  setPrescaler(1, divisor);
  setPrescaler(2, divisor);

  pinMode(MONITOR_PIN, OUTPUT);
  // stepper0.moveTo(DEGREES_TO_STEPS(360));
  // stepper1.moveTo(DEGREES_TO_STEPS(-360));
  stepper0.moveTo(0);
  stepper1.moveTo(0);

  Wire.begin(2);                // join i2c bus with address 
  Wire.onReceive(i2cReceiveEvent);  
}

uint8_t i2cReceiveBuffer[96];
void i2cReceiveEvent(int howMany)
{
  if(howMany == 25) {
    int index = Wire.read();
    Serial.println(index);
    int size = Wire.readBytes(&i2cReceiveBuffer[index*24], 24);
    if(index == 3)
    {
      /*
      Serial.println("Full update");

      for(int i=0;i<96;i++) {
        Serial.print(i);
        Serial.print("\t");
        Serial.println(i2cReceiveBuffer[i]);
      }
      */

      int16_t *i2cProcessPtr = (int16_t*)(&i2cReceiveBuffer[(MOTOR_ROW * 8 + MOTOR_COL) * 4]);
      int x0 = i2cProcessPtr[0];
      int x1 = i2cProcessPtr[1];
      // Serial.println(i2cReceiveBuffer
      Serial.println(x0);
      Serial.println(x1);
      stepper0.moveTo(DEGREES_TO_STEPS(x0)); 
      stepper1.moveTo(DEGREES_TO_STEPS(x1)); 
    }
  }
  else
  {
    Serial.println("i2c error");
    while(Wire.available()) // loop through all but the last
    {
      int c = Wire.read(); // receive byte as a character
      Serial.println(c);         // print the character
    }
  }
}

void loop(void)
{  
  //delay(1);
  
  stepper0.run();
  stepper1.run();
}
