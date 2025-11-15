#include "gcode_parser.hpp"
#include <string.h>
#include <stdlib.h>

GCodeCommand GCodeParser::parse(const char* line) {
    GCodeCommand cmd;

    // Skip whitespace
    while (*line == ' ' || *line == '\t') line++;

    // Skip comments
    if (*line == ';' || *line == '\0') {
        cmd.error = true;
        cmd.errorMsg = "Empty or comment";
        return cmd;
    }

    // Determine command type
    if (strncmp(line, "G0", 2) == 0) {
        cmd.type = CMD_G0;
    } else if (strncmp(line, "G1", 2) == 0) {
        cmd.type = CMD_G1;
    } else if (strncmp(line, "G28", 3) == 0) {
        cmd.type = CMD_G28;
        return cmd;  // No parameters needed
    } else if (strncmp(line, "M3", 2) == 0) {
        cmd.type = CMD_M3;
        return cmd;
    } else if (strncmp(line, "M5", 2) == 0) {
        cmd.type = CMD_M5;
        return cmd;
    } else {
        cmd.error = true;
        cmd.errorMsg = "Unknown G-code";
        return cmd;
    }

    // Parse coordinates for G0/G1
    if (hasLetter(line, 'X')) {
        cmd.x = parseValue(line, 'X');
    }
    if (hasLetter(line, 'Y')) {
        cmd.y = parseValue(line, 'Y');
    }
    if (hasLetter(line, 'F')) {
        cmd.feedRate = parseValue(line, 'F');
    }

    return cmd;
}

float GCodeParser::parseValue(const char* line, char letter) {
    // Find the letter
    const char* pos = strchr(line, letter);
    if (!pos) return 0.0;

    // Parse the number after the letter
    return atof(pos + 1);
}

bool GCodeParser::hasLetter(const char* line, char letter) {
    return strchr(line, letter) != nullptr;
}