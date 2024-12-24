#include <Arduino.h>
#include "AccelStepper.h"

#include "MotorVID28.h"

#define NUM_STEPS (360*3)
MotorVID28 motor(NUM_STEPS, false, 9, 10, 11);

#define multiMotorScaleTest 1

#if multiMotorScaleTest
MotorVID28 motor2(NUM_STEPS, false, 1, 2, 3);
MotorVID28 motor3(NUM_STEPS, false, 4, 5, 6);
MotorVID28 motor4(NUM_STEPS, false, 12, 13, 14);
MotorVID28 motor5(NUM_STEPS, false, 15, 16, 17);
MotorVID28 motor6(NUM_STEPS, false, 18, 19, 20);
MotorVID28 motor7(NUM_STEPS, false, 21, 22, 23);
MotorVID28 motor8(NUM_STEPS, false, 24, 25, 26);
#endif

// Create callback handlers, and instantiate an AccelStepper object

void stepper_fw() { motor.stepUp(); }
void stepper_bw() { motor.stepDown(); }
AccelStepper stepper(stepper_fw, stepper_bw);


#if multiMotorScaleTest

void stepper2_fw() { motor2.stepUp(); }
void stepper2_bw() { motor2.stepDown(); }
AccelStepper stepper2(stepper2_fw, stepper2_bw);

void stepper3_fw() { motor3.stepUp(); }
void stepper3_bw() { motor3.stepDown(); }
AccelStepper stepper3(stepper3_fw, stepper3_bw);

void stepper4_fw() { motor4.stepUp(); }
void stepper4_bw() { motor4.stepDown(); }
AccelStepper stepper4(stepper4_fw, stepper4_bw);

void stepper5_fw() { motor5.stepUp(); }
void stepper5_bw() { motor5.stepDown(); }
AccelStepper stepper5(stepper5_fw, stepper5_bw);

void stepper6_fw() { motor6.stepUp(); }
void stepper6_bw() { motor6.stepDown(); }
AccelStepper stepper6(stepper6_fw, stepper6_bw);

void stepper7_fw() { motor7.stepUp(); }
void stepper7_bw() { motor7.stepDown(); }
AccelStepper stepper7(stepper7_fw, stepper7_bw);

void stepper8_fw() { motor8.stepUp(); }
void stepper8_bw() { motor8.stepDown(); }
AccelStepper stepper8(stepper8_fw, stepper8_bw);

#endif



void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.print("Enter a step position from 0 through ");
  Serial.print(NUM_STEPS);
  Serial.println(".");

  //setPrescaler(1, 1);
  //setPrescaler(2, 1);

  stepper.setMaxSpeed(500.0);
  stepper.setAcceleration(75.0);
}

void loop(void)
{
  static int nextPos = 0;
  // the motor only moves when you call run()
  stepper.run();
  
#if multiMotorScaleTest
  stepper2.run();
  stepper3.run();
  stepper4.run();
  stepper5.run();
  stepper6.run();
  stepper7.run();
  stepper8.run();
#endif

  if (Serial.available()) {
    char c = Serial.read();
    if (c==10 || c==13) {
      //motor1.setPosition(nextPos);
      stepper.moveTo(nextPos);
      //stepper.setSpeed(5000.0);
      nextPos = 0;
    } else if (c>='0' && c<='9') {
      nextPos = 10*nextPos + (c-'0');
    } else if (c=='t') {
      Serial.println("Starttime");
      Serial.print(millis());
      Serial.print(" - ");
      Serial.println(micros());

      // stepper.runToNewPosition(stepper.currentPosition()+1080);
      nextPos = stepper.currentPosition() + NUM_STEPS;
      //stepper.moveTo();
      // while (stepper.distanceToGo() > 0){
      //   stepper.run();
      // }

      Serial.print(millis());
      Serial.print(" - ");
      Serial.println(micros());
    }
  }
}
