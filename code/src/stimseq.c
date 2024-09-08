#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

#include "stimseq.h"
#include "arg_parser.h"
#include "logger.h"
#include "sequence_parser.h"
#include "sequence_loader.h"

static bool ask_sequence_file_path(char *sequence_file_path);
static void init_logger(char* exe_path);



int main(int argc, char **argv)
{
    TimeStep *sequence = (TimeStep *) malloc(0);
    int sequence_size = 0;

    // Parse cli arguments
    ParsedArgs cli_args = parse_arguments(argc, argv);

    // Init log file
    init_logger(argv[0]);

    // Exit early if invalid arguments were given
    if (cli_args.all_args_valid == false)
    {
        return -1;
    }

    printf("********************************\n");
    printf("***** Welcome to StimSeq %s ****\n", STIMSEQ_VERSION);
    printf("********************************\n");

    // Ask the user to manually specify a sequence file if none were given through cli
    if (strcmp(cli_args.path, "") == 0)
    {
        if (!ask_sequence_file_path(cli_args.path))
        {
            print_log(ERROR, "No valid log file were given, exit...");
            return -1;
        }
    }

    // Parse the sequence file and exit in case of error
    sequence_size = parse_sequence_file(cli_args.path, &sequence);
    if (sequence_size <= 0)
    {
        goto Error;
    }

    if (!run_sequence(sequence, sequence_size))
    {
        goto Error;
    }

    // Free memory used to store sequence
    free(sequence);

    return 0;
Error:

    // Free memory used to store sequence
    free(sequence);
    return -1;

}

// Method to ask the user to manually enter a path, up to 3 time
static bool ask_sequence_file_path(char *sequence_file_path)
{
    int i;
    for (i = 0; i < 3; i ++)
    {
        printf("Enter the path to the sequence file tu use (Max 255 char) :\n");
        scanf("%s", sequence_file_path);

        if (check_path_valid(sequence_file_path) == false)
        {
            printf("ERROR: %s , file not found\n", sequence_file_path);
        } 
        else 
        {
            // The path is valid, thus stop asking.
            break;
        }
    }

    if (i == 3)
    {
        return false;
    }
    
    return true;
}

static void init_logger(char* exe_path)
{
    // Init Logger
    char * log_path = malloc(sizeof(exe_path) + sizeof("_log.txt"));
    strcpy(log_path, exe_path);
    strcat(log_path, "_log.txt");
    set_log_file(log_path);
    init_log_file();
    free(log_path);

}