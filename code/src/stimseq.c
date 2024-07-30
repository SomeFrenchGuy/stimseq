#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#include "stimseq.h"
#include "arg_parser.h"

#include "logger.h"

/* Generic Example using DAQmx */

int main(int argc, char **argv)
{
    //printf("Welcome to StimSeq\n");
    ParsedArgs cli_args = parse_arguments(argc, argv);

    set_log_file("./log.txt");
    init_log_file();

    print_log(INFO, "Test");
    print_log(WARNING, "Test");
    print_log(DEBUG, "Test");
    print_log(ERROR, "Test");


    // Exit early if invalid arguments were given
    if (cli_args.all_args_valid == false)
    {
        return 0;
    }

    return 0;
}