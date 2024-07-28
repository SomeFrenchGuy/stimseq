#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#include "arg_parser.h"
#include "stimseq.h"

/* Generic Example using DAQmx */

int main(int argc, char **argv)
{
    ParsedArgs cli_args = parse_arguments(argc, argv);

    // Exit early if invalid arguments were given
    if (cli_args.all_args_valid == false)
    {
        return 0;
    }

    return 0;
}