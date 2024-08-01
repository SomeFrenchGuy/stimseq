#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>

#include "stimseq.h"
#include "arg_parser.h"
#include "logger.h"
#include "sequence_parser.h"

bool ask_sequence_file_path(char *sequence_file_path);
void init_logger(char* exe_path);

int main(int argc, char **argv)
{
    ParsedArgs cli_args = parse_arguments(argc, argv);
    TimeStep *sequence = NULL;

    printf("********************************\n");
    printf("****** Welcome to StimSeq ******\n");
    printf("********************************\n");

    // Init log file
    init_logger(argv[0]);

    // Exit early if invalid arguments were given
    if (cli_args.all_args_valid == false)
    {
        print_log(ERROR, "Incorrect command line arguments were given");
        return -1;
    }

    if (strcmp(cli_args.path, "") == 0)
    {
        if (!ask_sequence_file_path(cli_args.path))
        {
            print_log(ERROR, "No valid log file were given, exit...");
            return -1;
        }
    }

    parse_sequence_file(cli_args.path, sequence);

    return 0;
}

// Method to ask the user to manually enter a path, up to 3 time
bool ask_sequence_file_path(char *sequence_file_path)
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
        print_log(ERROR, "No valid log file were given, exit...");
        return -1;
    }
    
    return true;
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