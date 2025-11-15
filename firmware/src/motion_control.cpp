#include "motion_control.hpp"
#include "config.hpp"
#include <Arduino.h>

MotionControl::MotionControl()
    : stepperX(STEPS_PER_REV, STEPPER_X_PORT),
      stepperY(STEPS_PER_REV, STEPPER_Y_PORT),
      currentX(0), currentY(0) {
}

void MotionControl::init() {
    stepperX.setSpeed(MOTOR_RPM);
    stepperY.setSpeed(MOTOR_RPM);
    stepperX.release();
    stepperY.release();
}

bool MotionControl::moveTo(float x, float y, float feedRate) {
    // Calculate steps needed
    int targetStepsX = mmToSteps(x);
    int targetStepsY = mmToSteps(y);

    int currentStepsX = mmToSteps(currentX);
    int currentStepsY = mmToSteps(currentY);

    int deltaX = targetStepsX - currentStepsX;
    int deltaY = targetStepsY - currentStepsY;

    // Check limits
    if (targetStepsX < 0 || targetStepsX > MAX_X_STEPS ||
        targetStepsY < 0 || targetStepsY > MAX_Y_STEPS) {
        return false;
    }

    // Execute movement
    moveSteps(deltaX, deltaY);

    // Update position
    currentX = x;
    currentY = y;

    return true;
}

bool MotionControl::home() {
    // Simple homing - just go to 0,0
    // In a real system, you'd use limit switches
    return moveTo(0, 0);
}

void MotionControl::setPosition(float x, float y) {
    currentX = x;
    currentY = y;
}

void MotionControl::getPosition(float& x, float& y) {
    x = currentX;
    y = currentY;
}

void MotionControl::moveSteps(int stepsX, int stepsY) {
    // Simple simultaneous movement
    int absX = abs(stepsX);
    int absY = abs(stepsY);
    int maxSteps = max(absX, absY);

    int dirX = (stepsX > 0) ? FORWARD : BACKWARD;
    int dirY = (stepsY > 0) ? FORWARD : BACKWARD;

    for (int i = 0; i < maxSteps; i++) {
        if (i < absX) {
            stepperX.step(1, dirX, DOUBLE);
        }
        if (i < absY) {
            stepperY.step(1, dirY, DOUBLE);
        }
    }

    // Release motors to save power
    stepperX.release();
    stepperY.release();
}

int MotionControl::mmToSteps(float mm) {
    return (int)(mm * STEPS_PER_MM);
}