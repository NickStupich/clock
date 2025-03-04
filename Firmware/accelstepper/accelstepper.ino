#include <Arduino.h>
#include "AccelStepper.h"

#include "MotorVID28.h"
#include "util.h"
#include <Wire.h>

#include "pins_arduino.h"

#define MOTOR_ROW 0
#define MOTOR_COL 7

#define MOTOR0_INDEX ((MOTOR_ROW * 8 + MOTOR_COL) * 2)
#define MOTOR1_INDEX ((MOTOR_ROW * 8 + MOTOR_COL) * 2 + 1)

#define PYTHON_MODULUS(n,m) (((n % m) + m) % m)  

#define STEPS_PER_STEP ((long)(MOTORVID28_NUM_MICROSTEPS / 6))
#define TIMER_ADJUSTMENT_FACTOR 64.0

#define DEGREES_TO_STEPS(x)  (3L*x * STEPS_PER_STEP)
#define STEPS_TO_DEGREES(x) (x / 3L / STEPS_PER_STEP)
#define NUM_STEPS (DEGREES_TO_STEPS(360))

#define HAND_SPEED (DEGREES_TO_STEPS(360) / 8.0 / TIMER_ADJUSTMENT_FACTOR)
#define HAND_ACCELERATION (DEGREES_TO_STEPS(45) / (TIMER_ADJUSTMENT_FACTOR * TIMER_ADJUSTMENT_FACTOR))

MotorVID28 motor0(NUM_STEPS, true, 6, 3, 5);
MotorVID28 motor1(NUM_STEPS, true, 11, 9, 10);

int target0 = 0;
int target1 = 0;

int calibrationSteps0 = 0;
int calibrationSteps1 = 0;

void stepper0_fw() { motor0.stepDown();}
void stepper0_bw() { motor0.stepUp(); }

void stepper1_fw() { motor1.stepDown(); }
void stepper1_bw() { motor1.stepUp(); }

AccelStepper stepper0(stepper0_bw, stepper0_fw);
AccelStepper stepper1(stepper1_bw, stepper1_fw);

void setup() {
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
  
  Wire.begin(2);                // join i2c bus with address 
  Wire.onReceive(i2cReceiveEvent);  

  // stepper0.moveTo(DEGREES_TO_STEPS(-179));
  // stepper1.moveTo(DEGREES_TO_STEPS(-360));
}

uint8_t i2cReceiveBuffer[64];
void i2cReceiveEvent(int howMany)
{
  int batch_index = Wire.read();

  if(howMany == 25 && batch_index == 10) //new calibration values, in 1/10ths of a degree
  {
    int size = Wire.readBytes(i2cReceiveBuffer, 24);
    calibrationSteps0 += DEGREES_TO_STEPS(*(int8_t*)(&i2cReceiveBuffer[MOTOR0_INDEX])) / 10;
    calibrationSteps1 += DEGREES_TO_STEPS(*(int8_t*)(&i2cReceiveBuffer[MOTOR1_INDEX])) / 10;
    Serial.print("new calibration (steps): ");
    Serial.print(calibrationSteps0);
    Serial.print("\t");
    Serial.print(calibrationSteps1);
    Serial.println("");
  }
  else if(howMany % 3 == 1) { //length 3 + cmd byte
    int size = Wire.readBytes(i2cReceiveBuffer, howMany-1);
    for(int i=0;i<size;i+=3) {
      uint8_t index = i2cReceiveBuffer[i];
      //Serial.print(index);
      int16_t *value = (int16_t*)(&i2cReceiveBuffer[i+1]);
      if(index == MOTOR0_INDEX) {
        target0 = *value;
        //Serial.print("M0 -> ");
        //Serial.println(target0);
        stepper0.moveTo(DEGREES_TO_STEPS(target0) + calibrationSteps0); 
      }
      else if(index == MOTOR1_INDEX) {
        target1 = *value;
        //Serial.print("M1 -> ");
        //Serial.println(target1);
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
  delay(1);
  
  bool running0 = stepper0.run();
  bool running1 = stepper1.run();

  if(!running0 && lastRunning0) {
      long position0 = stepper0.currentPosition() - calibrationSteps0;
      long newPosition0 = PYTHON_MODULUS(position0, DEGREES_TO_STEPS(360));
      Serial.print("motor 0 ");
      Serial.print(STEPS_TO_DEGREES(position0));
      Serial.print(" -> ");
      Serial.println(STEPS_TO_DEGREES(newPosition0));
      stepper0.setCurrentPosition(newPosition0 + calibrationSteps0);
  }
  lastRunning0 = running0;
  
  if(!running1 && lastRunning1) {
      long position1 = stepper1.currentPosition() - calibrationSteps1;
      long newPosition1 = PYTHON_MODULUS(position1, DEGREES_TO_STEPS(360));
      Serial.print("motor 1 ");
      Serial.print(STEPS_TO_DEGREES(position1));
      Serial.print(" -> ");
      Serial.println(STEPS_TO_DEGREES(newPosition1));
      stepper1.setCurrentPosition(newPosition1 + calibrationSteps1);
  }
  lastRunning1 = running1;
}
