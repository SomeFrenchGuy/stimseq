#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <getopt.h>

#include "arg_parser.h"


bool check_path_valid(const char *path);

ParsedArgs parse_arguments(int argc, char **argv)
{
    int option = 0;

    ParsedArgs arguments = {true, "", ""};

    while ((option = getopt(argc, argv, "p:l:h")) != -1)
    {
        switch (option)
        {
        case 'p':
            if(optarg != NULL)
            {
                strcpy(arguments.path, optarg);

                if (check_path_valid(arguments.path) == false)
                {
                    printf("ERROR: %s , file not found\n", arguments.path);
                    arguments.all_args_valid = false;
                }
            }
            break;
        
        case 'l':
            if(optarg != NULL)
            {
                strcpy(arguments.loglevel, optarg);

                if ((strcmp(arguments.loglevel, "WARNING") != 0) && (strcmp(arguments.loglevel, "DEBUG") != 0))
                {
                    printf("ERROR: %s is not a valid log level\n", arguments.loglevel);
                    printf("       Valid values are 'WARNING' and 'DEBUG'\n");
                    arguments.all_args_valid = false;
                }
            }
            break;

        case 'h':
        default:
            arguments.all_args_valid = false;
            printf("Usage: stimseq [OPTIONS]\n");
            printf(" -h for help\n");
            printf(" -p [path] to chose a sequence file\n");
            printf(" -l [log level] to specify a log level (WARNING, DEBUG)\n");
            break;
        }
    }

    return arguments;
}


// Check if path is a valid file
bool check_path_valid(const char *path)
{
    FILE *file = fopen(path, "r");

    if (file == NULL)
    {
        return false;
    }

    fclose(file);

    return true;
}