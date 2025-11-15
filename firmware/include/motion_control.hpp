#ifndef MOTION_CONTROL_HPP
#define MOTION_CONTROL_HPP

#include <AFMotor.h>

class MotionControl {
public:
    MotionControl();
    void init();
    bool moveTo(float x, float y, float feedRate = 1000);
    bool home();
    void setPosition(float x, float y);
    void getPosition(float& x, float& y);

private:
    AF_Stepper stepperX;
    AF_Stepper stepperY;

    float currentX;
    float currentY;

    void moveSteps(int stepsX, int stepsY);
    int mmToSteps(float mm);
};

#endif