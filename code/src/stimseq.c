#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>

#include "stimseq.h"
#include "arg_parser.h"

#include "logger.h"


void init_logger(char* exe_path);

int main(int argc, char **argv)
{
    ParsedArgs cli_args = parse_arguments(argc, argv);

    printf("Welcome to StimSeq\n");

    init_logger(argv[0]);

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

void init_logger(char* exe_path)
{
    // Init Logger
    char * log_path = malloc(sizeof(exe_path) + sizeof("_log.txt"));
    strcpy(log_path, exe_path);
    strcat(log_path, "_log.txt");
    set_log_file(log_path);
    init_log_file();
    free(log_path);

}