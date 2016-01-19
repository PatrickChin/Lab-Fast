#define _GNU_SOURCE
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <math.h>
#include <ctype.h>
#include <string.h>

int request_abort();

typedef struct muon_measurement {
    unsigned int decay_time;
    unsigned long time_stamp;
} mm;

long long atoll2(char** str);
void muon_parse_str(char* str, mm** data, int* nrows);
ssize_t muon_read_file(mm** data, int* size, char* file, int ascii);
ssize_t muon_write_binary(mm** data, int size, char* file);


