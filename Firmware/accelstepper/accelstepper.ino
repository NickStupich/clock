#include <Arduino.h>
#include "AccelStepper.h"

#include "MotorVID28.h"

#define NUM_STEPS (360*3)
#define NUM_MOTORS (8)

MotorVID28 motor1(NUM_STEPS, false, 9, 10, 11);
MotorVID28 motor2(NUM_STEPS, false, 1, 2, 3);
MotorVID28 motor3(NUM_STEPS, false, 4, 5, 6);
MotorVID28 motor4(NUM_STEPS, false, 12, 13, 14);
MotorVID28 motor5(NUM_STEPS, false, 15, 16, 17);
MotorVID28 motor6(NUM_STEPS, false, 18, 19, 20);
MotorVID28 motor7(NUM_STEPS, false, 21, 22, 23);
MotorVID28 motor8(NUM_STEPS, false, 24, 25, 26);

void stepper1_fw() { motor1.stepUp(); }
void stepper1_bw() { motor1.stepDown(); }

void stepper2_fw() { motor2.stepUp(); }
void stepper2_bw() { motor2.stepDown(); }

void stepper3_fw() { motor3.stepUp(); }
void stepper3_bw() { motor3.stepDown(); }

void stepper4_fw() { motor4.stepUp(); }
void stepper4_bw() { motor4.stepDown(); }

void stepper5_fw() { motor5.stepUp(); }
void stepper5_bw() { motor5.stepDown(); }

void stepper6_fw() { motor6.stepUp(); }
void stepper6_bw() { motor6.stepDown(); }

void stepper7_fw() { motor7.stepUp(); }
void stepper7_bw() { motor7.stepDown(); }

void stepper8_fw() { motor8.stepUp(); }
void stepper8_bw() { motor8.stepDown(); }

AccelStepper steppers[8] = {
  AccelStepper(stepper1_fw, stepper1_bw),
  AccelStepper(stepper2_fw, stepper2_bw),
  AccelStepper(stepper3_fw, stepper3_bw),
  AccelStepper(stepper4_fw, stepper4_bw),
  AccelStepper(stepper5_fw, stepper5_bw),
  AccelStepper(stepper6_fw, stepper6_bw),
  AccelStepper(stepper7_fw, stepper7_bw),
  AccelStepper(stepper8_fw, stepper8_bw)
};



void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.print("__Enter a step position from 0 through ");
  Serial.print(NUM_STEPS);
  Serial.println(".");

  //setPrescaler(1, 1);
  //setPrescaler(2, 1);

  for(int i=0;i<NUM_MOTORS;i++) {
    steppers[i].setMaxSpeed(500.0);
    steppers[i].setAcceleration(75.0);
  }
}

void loop(void)
{
  static int nextPos = 0;
  // the motor only moves when you call run()
  
  for(int i=0;i<NUM_MOTORS;i++) {
    steppers[i].run();
  }

  if (Serial.available()) {
    char c = Serial.read();
    if (c==10 || c==13) {
      steppers[0].moveTo(nextPos);
      nextPos = 0;
    } else if (c>='0' && c<='9') {
      nextPos = 10*nextPos + (c-'0');
    } else if (c=='t') {
      Serial.println("Starttime");
      Serial.print(millis());
      Serial.print(" - ");
      Serial.println(micros());

      nextPos = steppers[0].currentPosition() + NUM_STEPS;

      Serial.print(millis());
      Serial.print(" - ");
      Serial.println(micros());
    }
  }
}
