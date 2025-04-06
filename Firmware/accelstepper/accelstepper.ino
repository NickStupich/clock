#include <Arduino.h>
#include "AccelStepper.h"

#include "MotorVID28.h"
#include "util.h"
#include <Wire.h>

#include "pins_arduino.h"

#define MOTOR_ROW 2
#define MOTOR_COL 7
#define VERSION_STR "V6"

#define DEBUG_PRINTS 1

#define MOTOR0_INDEX ((MOTOR_ROW * 8 + MOTOR_COL) * 2)
#define MOTOR1_INDEX ((MOTOR_ROW * 8 + MOTOR_COL) * 2 + 1)
#define CALIBRATION_CMD_VALUE  (MOTOR0_INDEX < 24 ? 10 : 11)
#define CALIBRATION_INDEX0  (MOTOR0_INDEX % 24)
#define CALIBRATION_INDEX1  (MOTOR1_INDEX % 24)

#define PYTHON_MODULUS(n,m) (((n % m) + m) % m)  

#define STEPS_PER_STEP ((long)(MOTORVID28_NUM_MICROSTEPS / 6))
#define TIMER_ADJUSTMENT_FACTOR 64.0

#define DEGREES_TO_STEPS(x)  (3L*x * STEPS_PER_STEP)
#define STEPS_TO_DEGREES(x) (x / 3L / STEPS_PER_STEP)
#define NUM_STEPS (DEGREES_TO_STEPS(360))

#define HAND_SPEED_BASE (DEGREES_TO_STEPS(360) / 8.0 / TIMER_ADJUSTMENT_FACTOR)
#define HAND_ACCELERATION (DEGREES_TO_STEPS(45) / (TIMER_ADJUSTMENT_FACTOR * TIMER_ADJUSTMENT_FACTOR))

#define MAX_RAW_SPEED (256.0F)
#define BASE_RAW_SPEED (200.0F)
#define HAND_SPEED_RAW_TO_MULTIPLIER(raw) (raw == 0 ? MAX_RAW_SPEED / BASE_RAW_SPEED : ((float)raw) / BASE_RAW_SPEED)

MotorVID28 motor0(NUM_STEPS, true, 6, 3, 5);
MotorVID28 motor1(NUM_STEPS, true, 11, 9, 10);

long target0 = 0;
long target1 = 0;

long calibrationSteps0 = 0;
long calibrationSteps1 = 0;

uint8_t speedRaw0 = BASE_RAW_SPEED;
uint8_t speedRaw1 = BASE_RAW_SPEED;

#ifdef DEBUG_PRINTS
  long stepUp0Count = 0;
  long stepDown0Count = 0;
  long stepUp1Count = 0;
  long stepDown1Count = 0;
#endif

void stepper0_fw() { 
  #ifdef DEBUG_PRINTS
    stepDown0Count++;
  #endif
  motor0.stepDown();}

void stepper0_bw() { 
  #ifdef DEBUG_PRINTS
   stepUp0Count++;
  #endif
motor0.stepUp(); }

void stepper1_fw() { 
  #ifdef DEBUG_PRINTS
    stepDown1Count++;
  #endif
motor1.stepDown(); }

void stepper1_bw() { 
  #ifdef DEBUG_PRINTS
    stepUp1Count++;
  #endif
motor1.stepUp(); }

AccelStepper stepper0(stepper0_bw, stepper0_fw);
AccelStepper stepper1(stepper1_bw, stepper1_fw);

void setup() {
  Serial.begin(115200);
  Serial.print(VERSION_STR);
  Serial.print(" started for motor [");
  Serial.print(MOTOR_ROW);
  Serial.print(" , ");
  Serial.print(MOTOR_COL);
  Serial.println("]");

  stepper0.setMaxSpeed(HAND_SPEED_BASE);
  stepper0.setAcceleration(HAND_ACCELERATION);

  stepper1.setMaxSpeed(HAND_SPEED_BASE);
  stepper1.setAcceleration(HAND_ACCELERATION);
  
  int divisor = 1;
  setPrescaler(0, divisor);
  setPrescaler(1, divisor);
  setPrescaler(2, divisor);
  
  Wire.begin(2);                // join i2c bus with address 
  Wire.onReceive(i2cReceiveEvent);  

  //stepper0.moveTo(DEGREES_TO_STEPS(-179));
  // stepper1.moveTo(DEGREES_TO_STEPS(360));

  //stepper0.moveTo(DEGREES_TO_STEPS(4*360));
  //stepper1.moveTo(DEGREES_TO_STEPS(4*360));
}

uint8_t i2cReceiveBuffer[64];
void i2cReceiveEvent(int howMany)
{
  int batch_index = Wire.read();

  if(howMany == 25 && (batch_index == 10 || batch_index == 11)) //new calibration values, in 1/10ths of a degree
  {
    int size = Wire.readBytes(i2cReceiveBuffer, 24);
    if(batch_index == CALIBRATION_CMD_VALUE) {
      calibrationSteps0 += DEGREES_TO_STEPS(*(int8_t*)(&i2cReceiveBuffer[CALIBRATION_INDEX0])) / 10;
      calibrationSteps1 += DEGREES_TO_STEPS(*(int8_t*)(&i2cReceiveBuffer[CALIBRATION_INDEX1])) / 10;
      #ifdef DEBUG_PRINTS
        Serial.print("new calibration (steps): ");
        Serial.print(calibrationSteps0);
        Serial.print("\t");
        Serial.print(calibrationSteps1);
        Serial.println("");
      #endif
    }
  }
    
  else if(howMany % 4 == 1) { //length 3 + cmd byte
    int size = Wire.readBytes(i2cReceiveBuffer, howMany-1);
    for(int i=0;i<size;i+=4) {
      uint8_t index = i2cReceiveBuffer[i];
      //Serial.print(index);
      uint8_t newSpeedRaw = i2cReceiveBuffer[i+1];
      int16_t *value = (int16_t*)(&i2cReceiveBuffer[i+2]);
      if(index == MOTOR0_INDEX) {
        target0 = *value;
        #ifdef DEBUG_PRINTS
          Serial.print("M0 -> ");
          Serial.println(target0);
        #endif
        if(newSpeedRaw != speedRaw0) {
          
          stepper0.setMaxSpeed(HAND_SPEED_BASE * HAND_SPEED_RAW_TO_MULTIPLIER(newSpeedRaw));
          stepper0.setAcceleration(HAND_ACCELERATION);
          #ifdef DEBUG_PRINTS
            Serial.print("new speed0: ");
            Serial.print(newSpeedRaw);
            Serial.print("\t=\t");
            Serial.println(HAND_SPEED_RAW_TO_MULTIPLIER(newSpeedRaw));
          #endif
          speedRaw0 = newSpeedRaw;
        }
        stepper0.moveTo(DEGREES_TO_STEPS(target0) + calibrationSteps0); 
      }
      else if(index == MOTOR1_INDEX) {
        target1 = *value;
        #ifdef DEBUG_PRINTS
          Serial.print("M1 -> ");
          Serial.println(target1);
        #endif
        if(newSpeedRaw != speedRaw1) {
          stepper1.setMaxSpeed(HAND_SPEED_BASE * HAND_SPEED_RAW_TO_MULTIPLIER(newSpeedRaw));
          stepper1.setAcceleration(HAND_ACCELERATION);
          #ifdef DEBUG_PRINTS
            Serial.print("new speed1: ");
            Serial.print(newSpeedRaw);
            Serial.print("\t=\t");
            Serial.println(HAND_SPEED_RAW_TO_MULTIPLIER(newSpeedRaw));
          #endif
          speedRaw1 = newSpeedRaw;
        }
        stepper1.moveTo(DEGREES_TO_STEPS(target1) + calibrationSteps1); 
      }
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

bool lastRunning0 = false;
bool lastRunning1 = false;
void loop(void)
{  
 // delay(1);
  
  bool running0 = stepper0.run();
  bool running1 = stepper1.run();

  if(!running0 && lastRunning0) {
      long position0 = stepper0.currentPosition() - calibrationSteps0;
      long newPosition0 = PYTHON_MODULUS(position0, DEGREES_TO_STEPS(360));
      #ifdef DEBUG_PRINTS
        Serial.print("motor 0 ");
        Serial.print(STEPS_TO_DEGREES(position0));
        Serial.print(" -> ");
        Serial.println(STEPS_TO_DEGREES(newPosition0));
        
        Serial.print("Cal: ");
        Serial.println(calibrationSteps0);

        Serial.print("Step counts: ");
        Serial.print(stepUp0Count);
        Serial.print("\t");
        Serial.println(stepDown0Count);
        
        
      #endif
      stepper0.setCurrentPosition(newPosition0 + calibrationSteps0);
  }
  lastRunning0 = running0;
  
  if(!running1 && lastRunning1) {
      long position1 = stepper1.currentPosition() - calibrationSteps1;
      long newPosition1 = PYTHON_MODULUS(position1, DEGREES_TO_STEPS(360));
      
      #ifdef DEBUG_PRINTS
        Serial.print("motor 1 ");
        Serial.print(STEPS_TO_DEGREES(position1));
        Serial.print(" -> ");
        Serial.println(STEPS_TO_DEGREES(newPosition1));

        Serial.print("Cal: ");
        Serial.println(calibrationSteps1);
        
        Serial.print("Step counts: ");
        Serial.print(stepUp1Count);
        Serial.print("\t");
        Serial.println(stepDown1Count);
      #endif
      stepper1.setCurrentPosition(newPosition1 + calibrationSteps1);
  }
  lastRunning1 = running1;
}
