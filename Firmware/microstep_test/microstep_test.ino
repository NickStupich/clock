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
#define HAND_ACCELERATION (125 * STEPS_PER_STEP)

int frequencyTestPin = 13;

//int pin0 = 6, pin1 = 5, pin2= 7;
//int motor1State = 0;

// int stateCount = 24;
// static byte microStepState[] = {251, 238, 218, 191,
//                                 160, 128, 95, 64,
//                                 37, 17, 4, 0,
//                                 4, 17, 37, 64,
//                                 95, 128, 160, 191,
//                                 218, 238, 251, 255};


#define NUM_MOTORS 12

typedef struct  {
  const int pin0;
  const int pin1;
  const int pin2;
  int state;
  uint8_t pin0PWM;
  uint8_t pin1PWM;
  uint8_t pin2PWM;
  volatile uint8_t *out0;
  uint8_t bit0;
  volatile uint8_t *out1;
  uint8_t bit1;
  volatile uint8_t *out2;
  uint8_t bit2;
} Motor;

Motor motors[NUM_MOTORS] = {
  {3,2,4},  {6,5,7}, 
  {9,8,10},  {12,11,133}, 
  {55,54,56},  {58,57,59}, 
  {63,62,64},  {66,65,67}, 
  {31,33,29},  {25,27,23}, 
  {24,22,26},  {30, 28, 32}, 
  // {36,34,38},  {42, 40, 44}, 
  // {43,45,41},  {37, 39, 35}, 
};

                                
int stateCount = 24;
static byte microStepState[] = {0xff, 0xe, 0xd, 0xb,
                                0xa, 0x8, 0x5, 0x4,
                                0x2, 0x1, 0x0, 0x0,
                                0x0, 0x1, 0x2, 0x4,
                                0x5, 0x8, 0xa, 0xb,
                                0xd, 0xe, 0xff, 0xff};

// static byte microStepState[] = {0xff, 0xfe, 0xfe, 0xee,    //8,7,7,6
//                                 0xad, 0xaa, 0xa4, 0x44,    //5,4,3,2
//                                 0x08, 0x08, 0x00, 0x00,    //1,1,0,0
//                                 0x00, 0x08, 0x08, 0x44,    //0,1,1,2
//                                 0xa4, 0xaa, 0xad, 0xee,    //3,4,5,6
//                                 0xfe, 0xfe, 0xff, 0xff};  //7,7,8,8

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
  stepper_PWM(index);
}

void stepper_BW(int index) {
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

void stepper2_fw() { stepper_FW(2);}
void stepper2_bw() { stepper_BW(2);}
void stepper3_fw() { stepper_FW(3);}
void stepper3_bw() { stepper_BW(3);}

void stepper4_fw() { stepper_FW(4);}
void stepper4_bw() { stepper_BW(4);}
void stepper5_fw() { stepper_FW(5);}
void stepper5_bw() { stepper_BW(5);}

void stepper6_fw() { stepper_FW(6);}
void stepper6_bw() { stepper_BW(6);}
void stepper7_fw() { stepper_FW(7);}
void stepper7_bw() { stepper_BW(7);}

void stepper8_fw() { stepper_FW(8);}
void stepper8_bw() { stepper_BW(8);}
void stepper9_fw() { stepper_FW(9);}
void stepper9_bw() { stepper_BW(9);}

void stepper10_fw() { stepper_FW(10);}
void stepper10_bw() { stepper_BW(10);}
void stepper11_fw() { stepper_FW(11);}
void stepper11_bw() { stepper_BW(11);}

void stepper12_fw() { stepper_FW(12);}
void stepper12_bw() { stepper_BW(12);}
void stepper13_fw() { stepper_FW(13);}
void stepper13_bw() { stepper_BW(13);}

void stepper14_fw() { stepper_FW(14);}
void stepper14_bw() { stepper_BW(14);}
void stepper15_fw() { stepper_FW(15);}
void stepper15_bw() { stepper_BW(15);}


AccelStepper steppers[NUM_MOTORS] = 
{
  AccelStepper(stepper0_bw, stepper0_fw),
  AccelStepper(stepper1_bw, stepper1_fw),
  AccelStepper(stepper2_bw, stepper2_fw),
  AccelStepper(stepper3_bw, stepper3_fw),
  AccelStepper(stepper4_bw, stepper4_fw),
  AccelStepper(stepper5_bw, stepper5_fw),
  AccelStepper(stepper6_bw, stepper6_fw),
  AccelStepper(stepper7_bw, stepper7_fw),
  AccelStepper(stepper8_bw, stepper8_fw),
  AccelStepper(stepper9_bw, stepper9_fw),
  AccelStepper(stepper10_bw, stepper10_fw),
  AccelStepper(stepper11_bw, stepper11_fw),
  // AccelStepper(stepper12_bw, stepper12_fw),
  // AccelStepper(stepper13_bw, stepper13_fw),
  // AccelStepper(stepper14_bw, stepper14_fw),
  // AccelStepper(stepper15_bw, stepper15_fw),
};

void setup() {
  Serial.begin(9600);

      pinMode(frequencyTestPin, OUTPUT);
  // put your setup code here, to run once:

    for(int i=0;i<NUM_MOTORS;i++) {
      pinMode(motors[i].pin0, OUTPUT);
      pinMode(motors[i].pin1, OUTPUT);
      pinMode(motors[i].pin2, OUTPUT);

      motors[i].out0 = portOutputRegister(digitalPinToPort(motors[i].pin0));
      motors[i].bit0 = digitalPinToBitMask(motors[i].pin0);
      motors[i].out1 = portOutputRegister(digitalPinToPort(motors[i].pin1));
      motors[i].bit1 = digitalPinToBitMask(motors[i].pin1);
      motors[i].out2 = portOutputRegister(digitalPinToPort(motors[i].pin2));
      motors[i].bit2 = digitalPinToBitMask(motors[i].pin2);

      steppers[i].setMaxSpeed(HAND_SPEED);
      steppers[i].setAcceleration(HAND_ACCELERATION);
    }
    
    // steppers[0].moveTo(2222);
    // steppers[1].moveTo(2400);

    for(int i=0;i<NUM_MOTORS;i++) {
      steppers[i].moveTo(2000 + 200 * i);
    }
    
}

uint8_t PWM_MASK = 0xf;
uint8_t loopCount = 0;
void loop() {
  uint8_t pwmCount = loopCount & PWM_MASK;

  if((loopCount & 0xf) == 0) {
    digitalWrite(frequencyTestPin, loopCount & 0x10);
  }
      // Serial.println(pwmCount);
  /*
   if(pwmCount == 0) { //TODO: spread these out?
    for(int i=0;i<NUM_MOTORS;i++) {
      steppers[i].run();
      // Serial.println(motors[i].pin0PWM);
    }
   }*/
   
   uint8_t stepperCount = loopCount & 0x5;
   steppers[stepperCount << 1].run();
   steppers[(stepperCount << 1) + 1].run();

  for(int i=0;i<NUM_MOTORS;i++) {
    digitalWrite(motors[i].pin0, pwmCount >= motors[i].pin0PWM);
    digitalWrite(motors[i].pin1, pwmCount >= motors[i].pin1PWM);
    digitalWrite(motors[i].pin2, pwmCount >= motors[i].pin2PWM);

    
    // if (pwmCount >= motors[i].pin0PWM) {
    // // if(pwmCount & motors[i].pin0PWM) {
    //   *motors[i].out0 |= motors[i].bit0;
    // } else {
    //   *motors[i].out0 &= ~motors[i].bit0;
    // }
    
    // if (pwmCount >= motors[i].pin1PWM) {
    // // if(pwmCount & motors[i].pin1PWM) {
    //   *motors[i].out1 |= motors[i].bit1;
    // } else {
    //   *motors[i].out1 &= ~motors[i].bit1;
    // }
    
    // if (pwmCount >= motors[i].pin2PWM) {
    // // if(pwmCount & motors[i].pin2PWM) {
    //   *motors[i].out2 |= motors[i].bit2;
    // } else {
    //   *motors[i].out2 &= ~motors[i].bit2;
    // }
    
  }

  loopCount++;
}
