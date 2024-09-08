#ifndef __SEQUENCE_LOADER_
#define __SEQUENCE_LOADER_
#include <stdio.h>
#include <stdbool.h>

#include "sequence_parser.h"

bool load_sequence(const TimeStep * sequence, const int sequence_size);
bool run_sequence(const TimeStep * sequence, const int sequence_size);

#endif