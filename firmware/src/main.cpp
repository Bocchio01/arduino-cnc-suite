#include <Arduino.h>
#include <Servo.h>
#include <AFMotor.h>
#include "config.hpp"
#include "gcode_parser.hpp"
#include "motion_control.hpp"
#include "pen_control.hpp"

// Global objects
GCodeParser parser;
MotionControl motion;
PenControl pen;

// Command buffer
char commandBuffer[MAX_COMMAND_LENGTH];
int bufferIndex = 0;

void setup() {
    // Initialize serial
    Serial.begin(BAUD_RATE);
    while (!Serial) {
        ; // Wait for serial port to connect
    }

    // Initialize subsystems
    motion.init();
    pen.init();

    // Home position
    motion.setPosition(0, 0);
    pen.up();

    // Send ready signal
    Serial.println("READY");
}

void loop() {
    // Check for incoming data
    if (Serial.available() > 0) {
        char c = Serial.read();

        // Handle newline - execute command
        if (c == '\n' || c == '\r') {
            if (bufferIndex > 0) {
                commandBuffer[bufferIndex] = '\0';  // Null terminate
                executeCommand(commandBuffer);
                bufferIndex = 0;  // Reset buffer
            }
        }
        // Add character to buffer
        else if (bufferIndex < MAX_COMMAND_LENGTH - 1) {
            commandBuffer[bufferIndex++] = c;
        }
        // Buffer overflow - reset
        else {
            Serial.println("error: Buffer overflow");
            bufferIndex = 0;
        }
    }
}

void executeCommand(const char* command) {
    // Parse the command
    GCodeCommand cmd = parser.parse(command);

    // Handle errors
    if (cmd.error) {
        Serial.print("error: ");
        Serial.println(cmd.errorMsg);
        return;
    }

    // Execute based on command type
    bool success = false;

    switch (cmd.type) {
        case CMD_G0:  // Rapid positioning
        case CMD_G1:  // Linear move
            success = motion.moveTo(cmd.x, cmd.y, cmd.feedRate);
            break;

        case CMD_G28:  // Home
            success = motion.home();
            break;

        case CMD_M3:  // Pen down (spindle on)
            pen.down();
            success = true;
            break;

        case CMD_M5:  // Pen up (spindle off)
            pen.up();
            success = true;
            break;

        default:
            Serial.println("error: Unknown command");
            return;
    }

    // Send acknowledgment
    if (success) {
        Serial.println("ok");
    } else {
        Serial.println("error: Execution failed");
    }
}