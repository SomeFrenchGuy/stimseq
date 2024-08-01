
#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#include "sequence_parser.h"

// Max number of character in line
#define MAX_LINE_SIZE   512

// Parse the sequence
// Return the size of the sequence
// Don't FORGET TO FREE the space used by sequence when it's no longer used
int parse_sequence_file(char *file_path, TimeStep *sequence)
{
    FILE *seq_file = fopen(file_path, "r");
    unsigned int sequence_size = 0;
    char line[MAX_LINE_SIZE];
    char token[MAX_LINE_SIZE];

    TimeStep buf;

    while(fgets(line, MAX_LINE_SIZE, seq_file))
    {
        if(line[0] == '*')
        {
            continue;
        }
        sscanf(token, "%i,%b,%b,%b,%b,%b,%b,%b,%b,%i,%b", \
        buf.time, buf.valves[0], buf.valves[1], buf.valves[2], \
        buf.valves[3], buf.valves[4], buf.valves[5], buf.valves[6], \
        buf.valves[7], buf.led_voltage, buf.piezo_trigger);
        printf("%i,%b,%b,%b,%b,%b,%b,%b,%b,%i,%b\n", \
        buf.time, buf.valves[0], buf.valves[1], buf.valves[2], \
        buf.valves[3], buf.valves[4], buf.valves[5], buf.valves[6], \
        buf.valves[7], buf.led_voltage, buf.piezo_trigger);

        sequence_size ++;
    }



    fclose(seq_file);

    return (sequence_size);
}