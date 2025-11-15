#ifndef PEN_CONTROL_HPP
#define PEN_CONTROL_HPP

#include <Servo.h>

class PenControl {
public:
    void init();
    void up();
    void down();
    bool isDown();

private:
    Servo servo;
    bool penDown;
};

#endif