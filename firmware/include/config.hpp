#ifndef CONFIG_HPP
#define CONFIG_HPP

// Serial communication
#define BAUD_RATE 115200
#define MAX_COMMAND_LENGTH 64

// Servo configuration
#define SERVO_PIN 9
#define PEN_UP_ANGLE 90
#define PEN_DOWN_ANGLE 120
#define SERVO_DELAY 300  // ms to wait after servo movement

// Stepper configuration (AFMotor shield)
#define STEPPER_X_PORT 1  // M1/M2
#define STEPPER_Y_PORT 2  // M3/M4
#define STEPS_PER_REV 200
#define MOTOR_RPM 100

// Machine limits
#define MAX_X_STEPS 10000
#define MAX_Y_STEPS 10000

// Movement settings
#define STEPS_PER_MM 40.0  // Adjust based on your mechanics
#define DEFAULT_FEED_RATE 1000  // mm/min

#endif