#ifndef __SEQUENCE_PARSER_
#define __SEQUENCE_PARSER_

#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#include "stimseq.h"

typedef struct TimeStep
{
    unsigned int time;
    bool valves[VALVES_NUMBER];
    unsigned int led_voltage;
    bool piezo_trigger;
} TimeStep;


int parse_sequence_file(char *file_path, TimeStep **sequence);

#endif