#include <Arduino.h>
#include "AccelStepper.h"


#include <SPI.h>
#include "pins_arduino.h"

char buf [100];
volatile byte pos;

#define STEPS_PER_STEP (4)
#define DEGREES_TO_STEPS(x)  (3*x * STEPS_PER_STEP)
#define NUM_STEPS (DEGREES_TO_STEPS(360))
#define NUM_MOTORS (16)

#define HAND_SPEED (500 * STEPS_PER_STEP)
#define HAND_ACCELERATION (120 * STEPS_PER_STEP)

//int pin0 = 6, pin1 = 5, pin2= 7;
//int motor1State = 0;

// int stateCount = 24;
// static byte microStepState[] = {251, 238, 218, 191,
//                                 160, 128, 95, 64,
//                                 37, 17, 4, 0,
//                                 4, 17, 37, 64,
//                                 95, 128, 160, 191,
//                                 218, 238, 251, 255};


#define NUM_MOTORS 1

typedef struct  {
  const int pin0;
  const int pin1;
  const int pin2;
  int state;
  uint8_t pin0PWM;
  uint8_t pin1PWM;
  uint8_t pin2PWM;
} Motor;

Motor motors[NUM_MOTORS] = {
  // {3,2,4,0, 0, 0, 0},
  {6,5,7,0, 0, 0, 0},
};

                                
int stateCount = 24;
static byte microStepState[] = {0xff, 0xe, 0xd, 0xb,
                                0xa, 0x8, 0x5, 0x4,
                                0x2, 0x1, 0x0, 0x0,
                                0x0, 0x1, 0x2, 0x4,
                                0x5, 0x8, 0xa, 0xb,
                                0xd, 0xe, 0xff, 0xff};

#define HIGH_CONSTANT (0xff)
// static byte microStepState[] = {HIGH_CONSTANT, HIGH_CONSTANT, HIGH_CONSTANT, HIGH_CONSTANT,
//                                 HIGH_CONSTANT, HIGH_CONSTANT, 0x0, 0x0,
//                                 0x0, 0x0, 0x0, 0x0,
//                                 0x0, 0x0, 0x0, 0x0,
//                                 0x0, 0x0, HIGH_CONSTANT, HIGH_CONSTANT,
//                                 HIGH_CONSTANT, HIGH_CONSTANT, HIGH_CONSTANT, HIGH_CONSTANT};

#define STARTINDEX_PIN1 18 // 0 // 23-5
#define STARTINDEX_PIN23 10 // 23-13
#define STARTINDEX_PIN4 2 // 23-21

void stepper_FW(int index) {
  
  motors[index].state = (motors[index].state + 1) % stateCount;
  // motors[index].state -= 1;
  stepper_PWM(index);
}

void stepper_BW(int index) {
  // motors[index].state += 1;
  motors[index].state = (motors[index].state + (stateCount - 1)) % stateCount;
  stepper_PWM(index);
}

void stepper_PWM(int index) {
    motors[index].pin0PWM = microStepState[(motors[index].state+STARTINDEX_PIN1) % stateCount];
    motors[index].pin1PWM = microStepState[(motors[index].state+STARTINDEX_PIN23) % stateCount];
    motors[index].pin2PWM = microStepState[(motors[index].state+STARTINDEX_PIN4) % stateCount];
}

void stepper0_fw() { stepper_FW(0);}
void stepper0_bw() { stepper_BW(0);}
void stepper1_fw() { stepper_FW(1);}
void stepper1_bw() { stepper_BW(1);}

AccelStepper steppers[NUM_MOTORS] = 
{
  AccelStepper(stepper0_bw, stepper0_fw),
  // AccelStepper(stepper1_bw, stepper1_fw),
};

void setup() {
  Serial.begin(9600);
  // put your setup code here, to run once:

    for(int i=0;i<NUM_MOTORS;i++) {
      pinMode(motors[i].pin0, OUTPUT);
      pinMode(motors[i].pin1, OUTPUT);
      pinMode(motors[i].pin2, OUTPUT);

      steppers[i].setMaxSpeed(HAND_SPEED);
      steppers[i].setAcceleration(HAND_ACCELERATION);
    }
    
    // steppers[0].moveTo(2222);
    steppers[0].moveTo(2400);
}

uint8_t PWM_MASK = 0xf;
uint8_t loopCount = 0;
void loop() {
  uint8_t pwmCount = loopCount & PWM_MASK;
      // Serial.println(pwmCount);
  
   if(pwmCount == 0) {
    for(int i=0;i<NUM_MOTORS;i++) {
      steppers[i].run();
      // Serial.println(motors[i].pin0PWM);
    }
   }

  for(int i=0;i<NUM_MOTORS;i++) {
    digitalWrite(motors[i].pin0, pwmCount >= motors[i].pin0PWM);
    digitalWrite(motors[i].pin1, pwmCount >= motors[i].pin1PWM);
    digitalWrite(motors[i].pin2, pwmCount >= motors[i].pin2PWM);
  }

  loopCount++;

  //Serial.println(motor1State);

  // put your main code here, to run repeatedly:

  
}
