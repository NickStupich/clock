#include <Arduino.h>
#include "AccelStepper.h"

#include "MotorVID28.h"
#include "util.h"

#include <SPI.h>
#include "pins_arduino.h"

char buf [100];
volatile byte pos;

#define USE_ACCELSTEPPER 1
#define USE_MICROSTEPS 1

#define MONITOR_PIN 12

#if USE_MICROSTEPS
bool microstepMode = true;
#define STEPS_PER_STEP (MOTORVID28_NUM_MICROSTEPS / 6)
#else
bool microstepMode = false;
#define STEPS_PER_STEP (1)
#endif


#define DEGREES_TO_STEPS(x)  (3*x * STEPS_PER_STEP)
#define NUM_STEPS (DEGREES_TO_STEPS(360))
#define NUM_MOTORS (2)

#define HAND_SPEED (2.0 * STEPS_PER_STEP)
#define HAND_ACCELERATION (0.03 * STEPS_PER_STEP)

MotorVID28 motor1(NUM_STEPS, microstepMode, 5, 3, 6);
MotorVID28 motor2(NUM_STEPS, microstepMode, 10, 9, 11);
/*
// MotorVID28 motor1(NUM_STEPS, microstepMode, 3, 4, 2);
// MotorVID28 motor2(NUM_STEPS, microstepMode, 6, 7, 5);
// MotorVID28 motor1(NUM_STEPS, microstepMode, 55, 54, 56);
// MotorVID28 motor2(NUM_STEPS, microstepMode, 58, 57, 59);
MotorVID28 motor3(NUM_STEPS, microstepMode, 55, 54, 56);
MotorVID28 motor4(NUM_STEPS, microstepMode, 58, 57, 59);

// MotorVID28 motor1(NUM_STEPS, microstepMode, 33, 31, 35);
// MotorVID28 motor2(NUM_STEPS, microstepMode, 39, 37, 41);
MotorVID28 motor5(NUM_STEPS, microstepMode, 15, 16, 17);
MotorVID28 motor6(NUM_STEPS, microstepMode, 18, 19, 20);
MotorVID28 motor7(NUM_STEPS, microstepMode, 21, 22, 23);
MotorVID28 motor8(NUM_STEPS, microstepMode, 24, 25, 26);
MotorVID28 motor9(NUM_STEPS, microstepMode, 27, 28, 29);
MotorVID28 motor10(NUM_STEPS, microstepMode, 30, 31, 32);
MotorVID28 motor11(NUM_STEPS, microstepMode, 33, 34, 35);
MotorVID28 motor12(NUM_STEPS, microstepMode, 36, 37, 38);
MotorVID28 motor13(NUM_STEPS, microstepMode, 39, 40, 41);
MotorVID28 motor14(NUM_STEPS, microstepMode, 42, 43, 44);
MotorVID28 motor15(NUM_STEPS, microstepMode, 45, 46, 47);
MotorVID28 motor16(NUM_STEPS, microstepMode, 48, 49, 50);*/

#if USE_ACCELSTEPPER
  void stepper1_fw() { motor1.stepUp(); 
  digitalWrite(MONITOR_PIN, motor1.currentStep & 0x1); 
  }
  void stepper1_bw() { motor1.stepDown(); 
  digitalWrite(MONITOR_PIN, motor1.currentStep & 0x1);
  }

  void stepper2_fw() { motor2.stepUp(); }
  void stepper2_bw() { motor2.stepDown(); }
/*
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


  void stepper9_fw() { motor9.stepUp(); }
  void stepper9_bw() { motor9.stepDown(); }

  void stepper10_fw() { motor10.stepUp(); }
  void stepper10_bw() { motor10.stepDown(); }

  void stepper11_fw() { motor11.stepUp(); }
  void stepper11_bw() { motor11.stepDown(); }

  void stepper12_fw() { motor12.stepUp(); }
  void stepper12_bw() { motor12.stepDown(); }

  void stepper13_fw() { motor13.stepUp(); }
  void stepper13_bw() { motor13.stepDown(); }

  void stepper14_fw() { motor14.stepUp(); }
  void stepper14_bw() { motor14.stepDown(); }

  void stepper15_fw() { motor15.stepUp(); }
  void stepper15_bw() { motor15.stepDown(); }

  void stepper16_fw() { motor16.stepUp(); }
  void stepper16_bw() { motor16.stepDown(); }*/

  AccelStepper steppers[NUM_MOTORS] = {
    AccelStepper(stepper1_bw, stepper1_fw),
    AccelStepper(stepper2_bw, stepper2_fw),/*
    AccelStepper(stepper3_bw, stepper3_fw),
    AccelStepper(stepper4_bw, stepper4_fw),
    AccelStepper(stepper5_bw, stepper5_fw),
    AccelStepper(stepper6_bw, stepper6_fw),
    AccelStepper(stepper7_bw, stepper7_fw),
    AccelStepper(stepper8_bw, stepper8_fw),
    AccelStepper(stepper9_bw, stepper9_fw),
    AccelStepper(stepper10_bw, stepper10_fw),
    AccelStepper(stepper11_bw, stepper11_fw),
    AccelStepper(stepper12_bw, stepper12_fw),
    AccelStepper(stepper13_bw, stepper13_fw),
    AccelStepper(stepper14_bw, stepper14_fw),
    AccelStepper(stepper15_bw, stepper15_fw),
    AccelStepper(stepper16_bw, stepper16_fw)*/
  };
#else
  MotorVID28 motors[NUM_MOTORS] = {motor1, motor2, motor3, motor4, motor5, motor6, motor7, motor8, motor9, motor10, motor11, motor12, motor13, motor14, motor15, motor16};
  // MotorVID28 motors[NUM_MOTORS] = {motor1};
#endif

int16_t inputTargets[NUM_MOTORS*3+1]; //extra sync bytes at end
bool new_targets = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.println("Hello from nano");
  /*
  Serial.print("__Enter a step position from 0 through ");
  Serial.print(NUM_STEPS);
  Serial.println(".");
  */
  #if USE_ACCELSTEPPER
  for(int i=0;i<NUM_MOTORS;i++) {
    steppers[i].setMaxSpeed(HAND_SPEED);
    steppers[i].setAcceleration(HAND_ACCELERATION);
  }
  #else
  for(int i=0;i<NUM_MOTORS;i++) {
    motors[i].setMaxSpeed(HAND_SPEED/100);
  }

  #endif
    uint8_t mode = 1;
    
//#if USE_MICROSTEPS
    /*
    TCCR0B = TCCR0B & 0b11111000 | mode;
    TCCR1B = TCCR1B & 0b11111000 | mode;
    TCCR2B = TCCR2B & 0b11111000 | mode;

    TCCR3B = TCCR3B & 0b11111000 | mode;
    TCCR4B = TCCR4B & 0b11111000 | mode;
    TCCR5B = TCCR5B & 0b11111000 | mode;
    */
    int divisor = 1;
    setPrescaler(0, divisor);
    setPrescaler(1, divisor);
    setPrescaler(2, divisor);
  //#endif
/*
    // have to send on master in, *slave out*
  pinMode(MISO, OUTPUT);
  
  // turn on SPI in slave mode
  SPCR |= _BV(SPE);
  
  // turn on interrupts
  SPCR |= _BV(SPIE);
  
  pos = 0;

  SPI.attachInterrupt();

  */
      pinMode(MONITOR_PIN, OUTPUT);
      // steppers[1].moveTo(2200);
      //  steppers[0].moveTo(DEGREES_TO_STEPS(360));
      // steppers[1].moveTo(DEGREES_TO_STEPS(3600));
      steppers[1].moveTo(DEGREES_TO_STEPS(360));
  
    // for(int i=0;i<NUM_MOTORS;i++) {
    //   steppers[i].moveTo(DEGREES_TO_STEPS(360));
    // }
}


#define I2C_NUM_MOTOR_POSITIONS 16
// SPI interrupt routine
ISR (SPI_STC_vect)
{
  byte c = SPDR;  
  buf [pos++] = c;
  
  if(pos == (I2C_NUM_MOTOR_POSITIONS*2+2))
  {
      new_targets = true;
      for(int i=0;i<I2C_NUM_MOTOR_POSITIONS;i++) {
        byte c1 = buf[i*2];
        byte c2 = buf[i*2+1];

        int16_t c = (c1<<8) + c2;
        inputTargets[i] = c;
      }
      pos = 0;
  }
  
}

void loop(void)
{  
  delay(1);
  
  #if USE_ACCELSTEPPER
  for(int i=0;i<NUM_MOTORS;i++) {
    steppers[i].run();
  }
  #else

  for(int i=0;i<NUM_MOTORS;i++) {
    motors[i].update();
  }


  #endif


  if(new_targets) {
    Serial.println("new targets");
    for(int i=0;i<2;i++) {
      int x = DEGREES_TO_STEPS(inputTargets[i]);
      //x -= x % 24;
      Serial.print(inputTargets[i]);
      Serial.print("\t");
      Serial.println(x);

      #if USE_ACCELSTEPPER
        steppers[i].moveTo(x);
      #else
        motors[i].setPosition(x);
      #endif
    }
    Serial.println("\n");
    new_targets = false;
  }

  
  static int nextPos = 0;
  if (Serial.available()) {
    char c = Serial.read();
    if (c==10 || c==13) {
      #if USE_ACCELSTEPPER
      steppers[1].moveTo(nextPos);
      #else
      motors[1].setPosition(nextPos);
      #endif
      nextPos = 0;
    } else if (c>='0' && c<='9') {
      nextPos = 10*nextPos + (c-'0');
    } else if (c=='t') {
      Serial.println("Starttime");
      Serial.print(millis());
      Serial.print(" - ");
      Serial.println(micros());

      //nextPos = steppers[0].currentPosition() + NUM_STEPS;

      Serial.print(millis());
      Serial.print(" - ");
      Serial.println(micros());
    }
  }
  
}
