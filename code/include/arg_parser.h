#ifndef __ARG_PARSER_
#define __ARG_PARSER_

#include <stdio.h>
#include <stdbool.h>
#include "stimseq.h"

typedef struct ParsedArgs
{
    bool all_args_valid;
    char path[PATH_ARG_ZISE];
    char loglevel[LOGLVL_ARG_SIZE];
} ParsedArgs;

ParsedArgs parse_arguments(int argc, char **argv);

#endif