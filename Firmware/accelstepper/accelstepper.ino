#include <Arduino.h>
#include "AccelStepper.h"

#include "MotorVID28.h"

#include <SPI.h>
#include "pins_arduino.h"

char buf [100];
volatile byte pos;
volatile boolean process_it;

#define DEGREES_TO_STEPS(x)  (3*x)
#define NUM_STEPS (DEGREES_TO_STEPS(360))
#define NUM_MOTORS (16)

MotorVID28 motor1(NUM_STEPS, false, 9, 10, 11);
MotorVID28 motor2(NUM_STEPS, false, 1, 2, 3);
MotorVID28 motor3(NUM_STEPS, false, 4, 5, 6);
MotorVID28 motor4(NUM_STEPS, false, 12, 13, 14);
MotorVID28 motor5(NUM_STEPS, false, 15, 16, 17);
MotorVID28 motor6(NUM_STEPS, false, 18, 19, 20);
MotorVID28 motor7(NUM_STEPS, false, 21, 22, 23);
MotorVID28 motor8(NUM_STEPS, false, 24, 25, 26);
MotorVID28 motor9(NUM_STEPS, false, 27, 28, 29);
MotorVID28 motor10(NUM_STEPS, false, 30, 31, 32);
MotorVID28 motor11(NUM_STEPS, false, 33, 34, 35);
MotorVID28 motor12(NUM_STEPS, false, 36, 37, 38);
MotorVID28 motor13(NUM_STEPS, false, 39, 40, 41);
MotorVID28 motor14(NUM_STEPS, false, 42, 43, 44);
MotorVID28 motor15(NUM_STEPS, false, 45, 46, 47);
MotorVID28 motor16(NUM_STEPS, false, 48, 49, 50);

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
void stepper16_bw() { motor16.stepDown(); }

AccelStepper steppers[NUM_MOTORS] = {
  AccelStepper(stepper1_fw, stepper1_bw),
  AccelStepper(stepper2_fw, stepper2_bw),
  AccelStepper(stepper3_fw, stepper3_bw),
  AccelStepper(stepper4_fw, stepper4_bw),
  AccelStepper(stepper5_fw, stepper5_bw),
  AccelStepper(stepper6_fw, stepper6_bw),
  AccelStepper(stepper7_fw, stepper7_bw),
  AccelStepper(stepper8_fw, stepper8_bw),
  AccelStepper(stepper9_fw, stepper9_bw),
  AccelStepper(stepper10_fw, stepper10_bw),
  AccelStepper(stepper11_fw, stepper11_bw),
  AccelStepper(stepper12_fw, stepper12_bw),
  AccelStepper(stepper13_fw, stepper13_bw),
  AccelStepper(stepper14_fw, stepper14_bw),
  AccelStepper(stepper15_fw, stepper15_bw),
  AccelStepper(stepper16_fw, stepper16_bw)
};

int16_t inputTargets[NUM_MOTORS*3+1];// = {0}; //extra sync bytes
int inputTargetsIndex = 0;

bool new_targets = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.print("__Enter a step position from 0 through ");
  Serial.print(NUM_STEPS);
  Serial.println(".");

  Serial3.begin(9600);

  //setPrescaler(1, 1);
  //setPrescaler(2, 1);

  for(int i=0;i<NUM_MOTORS;i++) {
    steppers[i].setMaxSpeed(500.0);
    steppers[i].setAcceleration(120.0);
  }

    // have to send on master in, *slave out*
  pinMode(MISO, OUTPUT);
  
  // turn on SPI in slave mode
  SPCR |= _BV(SPE);
  
  // turn on interrupts
  SPCR |= _BV(SPIE);
  
  pos = 0;
  process_it = false;

  SPI.attachInterrupt();
}


// SPI interrupt routine
ISR (SPI_STC_vect)
{
byte c = SPDR;
//Serial.print(c);
  
    buf [pos++] = c;
    //Serial.println(pos);
    
    if(pos == (NUM_MOTORS*6+2))
    {
        new_targets = true;
        for(int i=0;i<NUM_MOTORS*3;i++) {
          byte c1 = buf[i*2];
          byte c2 = buf[i*2+1];

          int16_t c = (c1<<8) + c2;
          inputTargets[i] = c;

        }
        pos = 0;
    }
    // example: newline means time to process buffer
    /*if (c == 0xff)
      process_it = true;
      
    }  // end of room available
    */
    
}

void loop(void)
{
  static int nextPos = 0;
  // the motor only moves when you call run()
  
  for(int i=0;i<NUM_MOTORS;i++) {
    steppers[i].run();
  }

  if(new_targets) {
    Serial.println("new targets");
    for(int i=0;i<NUM_MOTORS*3;i++) {

         Serial.println(inputTargets[i]);
        
        steppers[0].moveTo(DEGREES_TO_STEPS(inputTargets[0]));

        }
        Serial.println("\n\n");
        new_targets = false;
  }
  else
  {
     //delay(100);
     //Serial.println(pos);
  }
  /*
  if (process_it)
    {
    buf [pos] = 0;  
    Serial.println (buf);
    pos = 0;
    process_it = false;
    }  // end of flag set
    else 
    { 
      //Serial.println(pos);
    }*/
  /*
  if(Serial1.available()) {
    unsigned char c1 = Serial1.read();
    Serial.println(c1);
  }
*/
/*
  if(Serial3.available() >= 2) {
    unsigned char c1 = Serial3.read();
    unsigned char c2 = Serial3.read();

    int16_t c = (c1<<8) + c2;
    
    Serial.print(inputTargetsIndex);
    Serial.print("\t\t");
    //Serial.println(c);
    Serial.print(c1);
    Serial.print("\t");
    Serial.println(c2);
    inputTargets[inputTargetsIndex] = c;
    inputTargetsIndex++;

    //Serial.print(c3);
    //Serial.print("\t");
    //Serial.print(inputTargetsIndex);
    //Serial.println("");
    //inputTargetsChar[inputTargetsIndex] = c3;
    //((unsigned char*)&inputTargets)[inputTargetsIndex] = c3;
    //inputTargetsIndex++;

    if(inputTargetsIndex == (NUM_MOTORS*3+1))
    {
      Serial.println("");
      Serial.println("full update");
      //Serial.print(inputTargets[NUM_MOTORS-1]);
      inputTargetsIndex = 0;

      steppers[0].moveTo(inputTargets[0]);
    }
  }*/

  if (Serial.available()) {
    char c = Serial.read();
    //Serial.print(c);
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
