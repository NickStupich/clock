#ifndef _CLOCK_STEPPER_H
#define _CLOCK_STEPPER_H

#define TIMER_ADJUSTMENT_FACTOR 64.0

enum AccelerationState {
  ACCELERATING,
  DECCELERATING,
  CONSTANT_MOTION,
  STOPPED //TODO: needed or constant motion?
};

class ClockStepper
{

 public:
   ClockStepper(void (*forward)(), void (*backward)());

    void setMaxSpeed(float stepsPerSecond);
    void setAcceleration(float acceleration);
    void moveTo(long position);

    long currentPosition(void);
    void setCurrentPosition(long newPosition);
    bool run(void);

  private:
    long targetSteps = 0;
    long currentSteps = 0;

    float maxSpeedStepsPerSec = 16.875;
    float accelerationStepsPerSec2 = 0.263671875;

    float currentSpeedStepsPerSec = 0;
    unsigned long lastStepMicros = 0;
    unsigned long nextStepDelayMicros = 0;

    //-1, +1 or 0 is stopped
    int moveDirection = 0;
    AccelerationState accelState = STOPPED;
    unsigned long stopAcceleratingMicros = 0;
    unsigned long startDecceleratingMicros = 0;

    void (*stepForward)();
    void (*stepBackward)();

    unsigned long time_micros(void);
};

#endif