#include "ClockStepper.h"

#include <Arduino.h>

ClockStepper::ClockStepper(void (*forward)(), void (*backward)())
{
  this->stepForward = forward;
  this->stepBackward = backward;
}

void ClockStepper::setMaxSpeed(float stepsPerSecond)
{
  maxSpeedStepsPerSec = stepsPerSecond;
  //TODO: anything else? won't apply til next move
}

void ClockStepper::setAcceleration(float acceleration)
{
  //TODO
}

void ClockStepper::moveTo(long position)
{
  unsigned long currentTimeMicros = time_micros();
  
  if(position > currentSteps) 
  {
    moveDirection = 1;
  } 
  else if (position < currentSteps) 
  {
    moveDirection = -1;
  }
  else
  {
    moveDirection = 0;
  }

  targetSteps = position;
  lastStepMicros = currentTimeMicros;
  nextStepDelayMicros = 0;


  //calculate acceleration/decceleration points
  long stepsToFinal = abs(targetSteps - currentSteps);
  Serial.print("stepsToFinal  ");
  Serial.println(stepsToFinal);
  
  float timeUpToTopSpeed = (maxSpeedStepsPerSec - currentSpeedStepsPerSec) / accelerationStepsPerSec2;
  Serial.print("timeUpToTopSpeed  ");
  Serial.println(timeUpToTopSpeed / TIMER_ADJUSTMENT_FACTOR);
  float distanceUpToTopSpeed = currentSpeedStepsPerSec * timeUpToTopSpeed + 0.5 * accelerationStepsPerSec2 * timeUpToTopSpeed * timeUpToTopSpeed;
  Serial.print("distanceUpToTopSpeed  ");
  Serial.println(distanceUpToTopSpeed);

  float timeToStop = maxSpeedStepsPerSec / accelerationStepsPerSec2;
  Serial.print("timeToStop  ");
  Serial.println(timeToStop/TIMER_ADJUSTMENT_FACTOR);
  float distanceToStop = maxSpeedStepsPerSec * timeToStop - 0.5 * accelerationStepsPerSec2 * timeToStop * timeToStop;
  Serial.print("distanceToStop  ");
  Serial.println(distanceToStop);

  float timeAtConstantSpeed = (stepsToFinal - distanceUpToTopSpeed - distanceToStop) / currentSpeedStepsPerSec;

  if((distanceToStop + distanceUpToTopSpeed) <= stepsToFinal) {
    Serial.println("Runs to full speed");
    //stopAcceleratingStep = currentSteps + distanceUpToTopSpeed;
    //startDecceleratingStep = targetSteps - distanceToStop;
    stopAcceleratingMicros = currentTimeMicros + timeUpToTopSpeed * 1000000;
    startDecceleratingMicros = currentTimeMicros + (timeUpToTopSpeed + timeAtConstantSpeed) * 1000000;
    accelState = ACCELERATING;
  }
  else if (distanceToStop <= stepsToFinal) //deccelerate right away. don't worry about the overshooting trying to smoothly deccelerate, we'll just hard stop
  {
    Serial.println("Deccelerate right away");
    accelState = ACCELERATING;

  }
  else //need to figure out smooth accel/deccel points when it doesn't fully get up to top speed 
  {  
    Serial.println("Doesn't reach full speed");

  }


  
}

long ClockStepper::currentPosition(void)
{
  return currentSteps;
}

void ClockStepper::setCurrentPosition(long newPosition)
{
  moveDirection = 0;
  currentSteps = newPosition;
  targetSteps = newPosition;
}

bool ClockStepper::run(void)
{
  // Serial.print("moveDir: ");
  // Serial.println(moveDirection);

  if(moveDirection != 0)
  {
    unsigned long currentTimeMicros = time_micros();

    //Serial.println("Times");
    //.println(currentTimeMicros);
    //Serial.println(lastStepMicros);
    //Serial.println(nextStepDelayMicros);

    if((long)(currentTimeMicros - lastStepMicros)>= nextStepDelayMicros) {
      unsigned long elapsedMicros = currentTimeMicros - lastStepMicros;

      //Serial.println("Step!");
      if(moveDirection > 0) {
        stepForward();
        currentSteps++;
      }
      else {
        stepBackward();
        currentSteps--;
      }

      if(currentSteps == targetSteps) 
      {
        moveDirection = 0;
        currentSpeedStepsPerSec = 0; //make sure exactly zero in case of rounding errors
      }
      else 
      {
        lastStepMicros += nextStepDelayMicros; //this may be in the past, but means we don't accumulate errors


        if(accelState == ACCELERATING) {

        } else if (accelState == CONSTANT_MOTION) {

        }
        else if (accelState == DECCELERATING) {

        }
        //todo: currentSpeed needs to be negative too so we can smoothly accelerate between movements in different directions
        //TODO: deccelerate
        currentSpeedStepsPerSec += moveDirection * ((float)elapsedMicros) * accelerationStepsPerSec2 / 1000000.0;
        if(abs(currentSpeedStepsPerSec) > maxSpeedStepsPerSec)
        {
          currentSpeedStepsPerSec = moveDirection * maxSpeedStepsPerSec;
        }

        
        //Serial.print("currentSpeedStepsPerSec: ");
        //Serial.println(currentSpeedStepsPerSec);
  

        nextStepDelayMicros = 1000000.0 / abs(currentSpeedStepsPerSec) + 0.5;//rounded to int
        nextStepDelayMicros = min(1000000, nextStepDelayMicros); //set a minimum speed to deal with very start/end of movements
      }
    }
    
    if(currentSteps == targetSteps) {
      moveDirection = 0;
    }
  } 
  
  return moveDirection != 0;
}

unsigned long ClockStepper::time_micros(void)
{
  //TODO: fix overflow
  unsigned long result = micros();
  
  // Serial.print("micros: ");
  // Serial.println(result);
  return result;
}