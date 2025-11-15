#include "pen_control.hpp"
#include "config.hpp"
#include <Arduino.h>

void PenControl::init() {
    servo.attach(SERVO_PIN);
    penDown = false;
    up();  // Start with pen up
}

void PenControl::up() {
    if (penDown) {
        servo.write(PEN_UP_ANGLE);
        delay(SERVO_DELAY);
        penDown = false;
    }
}

void PenControl::down() {
    if (!penDown) {
        servo.write(PEN_DOWN_ANGLE);
        delay(SERVO_DELAY);
        penDown = true;
    }
}

bool PenControl::isDown() {
    return penDown;
}