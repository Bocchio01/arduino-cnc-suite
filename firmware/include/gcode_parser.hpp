#ifndef GCODE_PARSER_HPP
#define GCODE_PARSER_HPP

enum CommandType {
    CMD_UNKNOWN,
    CMD_G0,   // Rapid positioning
    CMD_G1,   // Linear interpolation
    CMD_G28,  // Home
    CMD_M3,   // Pen down (spindle on)
    CMD_M5    // Pen up (spindle off)
};

struct GCodeCommand {
    CommandType type;
    float x;
    float y;
    float feedRate;
    bool error;
    const char* errorMsg;

    GCodeCommand() : type(CMD_UNKNOWN), x(0), y(0), feedRate(1000),
                     error(false), errorMsg(nullptr) {}
};

class GCodeParser {
public:
    GCodeCommand parse(const char* line);

private:
    float parseValue(const char* line, char letter);
    bool hasLetter(const char* line, char letter);
};

#endif