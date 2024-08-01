#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <stdlib.h>

#include "arg_parser.h"
#include "stimseq.h"

#include "logger.h"


static bool show_info = true;
static bool show_debug = true;
static bool show_warning = true;
static bool show_error = true;
static char log_file[255] = "./log.txt";


static void write_to_log_file(const char *data);

// Init an empty logfile.
// If the file already exists, replace it with an empty one
void init_log_file()
{
    FILE *file = fopen(log_file, "w");

    fclose(file);
}
// Set the log file
// Should be followed by a call to init_log_file
void set_log_file(const char* path_to_log_file)
{
    strcpy(log_file, path_to_log_file);

}


// A simple log function to log messages to a file
void print_log (LogLvl log_lvl, char *msg)
{
    // Initialize and get current time
    time_t t = time( NULL );

    // Allocate space for date string DON'T FORGET TO FREE
    char* date = (char*)malloc( 100 );

    // Format the time correctly
    strftime(date, 100, "[%F %T]", localtime(&t));

    // Allocate space for full_msg string DON'T FORGET TO FREE
    char* full_msg = (char*)malloc(sizeof(date) + sizeof(msg) + sizeof("[WARNING]: "));


    switch (log_lvl)
    {
    case INFO:
        if (show_info)
        {
            sprintf(full_msg, "%s[INFO]: %s\n", date, msg);
            printf("%s", full_msg);
            write_to_log_file(full_msg);
        }
        break;
    
    case WARNING:
        if (show_warning)
        {
            sprintf(full_msg, "%s[WARNING]: %s\n", date, msg);
            printf("%s", full_msg);
            write_to_log_file(full_msg);
        }
        break;
    
    case ERROR:
        if (show_error)
        {
            sprintf(full_msg, "%s[ERROR]: %s\n", date, msg);
            printf("%s", full_msg);
            write_to_log_file(full_msg);
        }
        break;
    
    case DEBUG:
        if (show_debug)
        {
            sprintf(full_msg, "%s[DEBUG]: %s\n", date, msg);
            printf("%s", full_msg);
            write_to_log_file(full_msg);
        }
        break;
    
    default:
        printf("WARNING: tried to log message with unknown log lvl\n");
        write_to_log_file("WARNING: tried to log message with unknown log lvl\n");
        break;
    }

    free(full_msg);
    free(date);
}

// Function to enable or disable the display of a specifi log lvl
void display_log_lvl(LogLvl log_lvl, bool show)
{
    switch (log_lvl)
    {
    case INFO:
        show_info = show;
        break;
    
    case WARNING:
        show_warning = show;
        break;
    
    case ERROR:
        show_error = show;
        break;
    
    case DEBUG:
        show_debug = show;
        break;
    
    default:
        break;
    }
}

// Write data to the log file
static void write_to_log_file(const char *data)
{
    FILE *file = fopen(log_file, "a");
    fprintf(file, "%s", data);
    fclose(file);
}