#ifndef __LOGGER_H_
#define __LOGGER_H_

#include <stdio.h>
#include <stdbool.h>
#include <string.h>

typedef enum LogLvl
{
    INFO,
    WARNING,
    ERROR,
    DEBUG
} LogLvl;

void init_log_file();
void set_log_file(const char* path_to_log_file);
void print_log(LogLvl log_lvl, const char* str, ... );
void display_log_lvl(LogLvl log_lvl, bool show);

#endif