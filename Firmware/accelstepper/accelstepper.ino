#include <Arduino.h>
#include "AccelStepper.h"

#include "MotorVID28.h"
#include "util.h"
#include <Wire.h>

#include "pins_arduino.h"

#define USE_MICROSTEPS 1
#define MONITOR_PIN 12

#define MOTOR_ROW 2
#define MOTOR_COL 7

#define MOTOR0_INDEX ((MOTOR_ROW * 8 + MOTOR_COL) * 2)
#define MOTOR1_INDEX ((MOTOR_ROW * 8 + MOTOR_COL) * 2 + 1)

//this is still untested!
#define PYTHON_MODULUS(n,m) (((n % m) + m) % m)  

#if USE_MICROSTEPS
bool microstepMode = true;
#define STEPS_PER_STEP ((long)(MOTORVID28_NUM_MICROSTEPS / 6))
#else
bool microstepMode = false;
#define STEPS_PER_STEP (1L)
#endif

#define TIMER_ADJUSTMENT_FACTOR 64.0

#define DEGREES_TO_STEPS(x)  (3L*x * STEPS_PER_STEP)
#define STEPS_TO_DEGREES(x) (x / 3L / STEPS_PER_STEP)
#define NUM_STEPS (DEGREES_TO_STEPS(360))

#define HAND_SPEED (DEGREES_TO_STEPS(360) / 8.0 / TIMER_ADJUSTMENT_FACTOR)
#define HAND_ACCELERATION (DEGREES_TO_STEPS(45) / (TIMER_ADJUSTMENT_FACTOR * TIMER_ADJUSTMENT_FACTOR))

MotorVID28 motor0(NUM_STEPS, microstepMode, 6, 3, 5);
MotorVID28 motor1(NUM_STEPS, microstepMode, 11, 9, 10);

int target0 = 0;
int target1 = 0;

void stepper0_fw() { motor0.stepDown();}
void stepper0_bw() { motor0.stepUp(); }

void stepper1_fw() { motor1.stepDown(); }
void stepper1_bw() { motor1.stepUp(); }

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
  
  Wire.begin(2);                // join i2c bus with address 
  Wire.onReceive(i2cReceiveEvent);  
}

uint8_t i2cReceiveBuffer[144];
void i2cReceiveEvent(int howMany)
{
  //Serial.print(howMany);
  if(howMany % 3 == 1) { //length 3 + cmd byte
    int batch_index = Wire.read();
    int size = Wire.readBytes(i2cReceiveBuffer, howMany-1);
    for(int i=0;i<size;i+=3) {
      uint8_t index = i2cReceiveBuffer[i];
      //Serial.print(index);
      int16_t *value = (int16_t*)(&i2cReceiveBuffer[i+1]);
      if(index == MOTOR0_INDEX) {
        //Serial.print("M0 -> ");
        target0 = *value;
        //Serial.println(target0);
        stepper0.moveTo(DEGREES_TO_STEPS(target0)); 
      }
      else if(index == MOTOR1_INDEX) {
        //Serial.print("M1 -> ");
        target1 = *value;
        //Serial.println(target1);
        stepper1.moveTo(DEGREES_TO_STEPS(target1)); 
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
      long position0 = stepper0.currentPosition();
      long newPosition0 = PYTHON_MODULUS(position0, DEGREES_TO_STEPS(360));
      Serial.print("motor 0 ");
      Serial.print(STEPS_TO_DEGREES(position0));
      Serial.print(" -> ");
      Serial.println(STEPS_TO_DEGREES(newPosition0));
      stepper0.setCurrentPosition(newPosition0);
  }
  lastRunning0 = running0;
  
  if(!running1 && lastRunning1) {
      long position1 = stepper1.currentPosition();
      long newPosition1 = PYTHON_MODULUS(position1, DEGREES_TO_STEPS(360));
      Serial.print("motor 1 ");
      Serial.print(STEPS_TO_DEGREES(position1));
      Serial.print(" -> ");
      Serial.println(STEPS_TO_DEGREES(newPosition1));
      stepper1.setCurrentPosition(newPosition1);
  }
  lastRunning1 = running1;
}
