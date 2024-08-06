
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>

#include "sequence_parser.h"
#include "logger.h"

// Max number of character in line
#define MAX_LINE_SIZE   512

// Number of column
#define COLUMNS_NB  11

// Parse the sequence
// Return the size of the sequence or -1 in case of error
// Don't FORGET TO FREE the space used by sequence when it's no longer used
int parse_sequence_file(char *file_path, TimeStep **sequence)
{
    print_log(INFO, "Parsing sequence file : %s", file_path);

    FILE *seq_file = fopen(file_path, "r");
    int sequence_size = 0;
    unsigned int row_number =0;
    char line[MAX_LINE_SIZE];

    int match_number;

    TimeStep buf;

    // Read line by line
    while(fgets(line, MAX_LINE_SIZE, seq_file))
    {
        row_number++;

        // Skip comment lines starting fith a * character
        if(line[0] == '*')
        {
            print_log(DEBUG, "Skipped Row %i (Comment)", row_number);
            continue;
        }

        // Parse line
        match_number = sscanf(line, "%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u", \
                                &buf.time,                              \
                                (unsigned int*) &buf.valves[0],         \
                                (unsigned int*) &buf.valves[1],         \
                                (unsigned int*) &buf.valves[2],         \
                                (unsigned int*) &buf.valves[3],         \
                                (unsigned int*) &buf.valves[4],         \
                                (unsigned int*) &buf.valves[5],         \
                                (unsigned int*) &buf.valves[6],         \
                                (unsigned int*) &buf.valves[7],         \
                                &buf.led_voltage,                       \
                                (unsigned int*) &buf.piezo_trigger);

        print_log(DEBUG,"Parsing row: %i\tNumber of element: %i\t Sequence Size: %i", row_number, match_number, sequence_size);
        if (match_number != COLUMNS_NB)
        {
            print_log(WARNING, "Skipped Row %i", row_number);
            continue;
        }


        // Add the parsed line to the sequence
        sequence_size ++;
        *sequence = (TimeStep *)realloc(*sequence, sequence_size * sizeof(TimeStep));
        (*sequence)[sequence_size - 1] = buf;
    }
    
    if(fclose(seq_file) != 0)
    {
        print_log(ERROR, "Error while closing log file after writting log");
        return -1;
    }
    return (sequence_size);
}