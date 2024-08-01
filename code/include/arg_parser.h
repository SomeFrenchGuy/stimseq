#ifndef __ARG_PARSER_
#define __ARG_PARSER_

#include <stdio.h>
#include <stdbool.h>

#include "stimseq.h"
#include "logger.h"

typedef struct ParsedArgs
{
    bool all_args_valid;
    char path[MAX_ARG_SIZE];
    char loglevel[MAX_ARG_SIZE];
} ParsedArgs;

ParsedArgs parse_arguments(int argc, char **argv);
bool check_path_valid(const char *path);

#endif