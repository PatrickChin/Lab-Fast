#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <math.h>
#include <ctype.h>

#include "atoll2.h"

typedef struct muon_measurement {
    unsigned int decay_time;
    unsigned long long time_stamp;
} mm;

/**
 * The only difference between this and the stdlib implementation
 * is that this function increments the `str` pointer.
 */
long long atoll2(char** str)
{
    // ignore leading whitespace
    while (isspace(**str)) (*str)++;

    long long val = 0;
    while (isdigit(**str))
        val = val*10 + (*(*str)++ - '0');

    return val;
}

mm* parse_ascii(char* c, int *nrows)
{
    *nrows = 1; // assuming the last line isn't empty
    char *pos = c;
    while (*pos)
        if (*pos++ == '\n')
            (*nrows)++;

    mm *data = (mm*) calloc(*nrows, sizeof(mm));
    for (int i = 0; i < *nrows; ++i)
    {
        data[i].decay_time = atoll2(&c);
        data[i].time_stamp = atoll2(&c);
        // printf("%3d %6i %10llu\n", i, data[i].decay_time, data[i].time_stamp);
    }

    printf("nrows: %d\n", *nrows);
    return data;
}

int main(int argc, char *argv[])
{
    if (argc < 3)
    {
        printf("TODO - useage");
        return -1;
    }

    int fd = open(argv[2], O_RDONLY);
    if (fd < 0)
    {
        printf("Failed to open \"%s\"\n", argv[1]);
        return -1;
    }

    struct stat fst;
    fstat(fd, &fst);

    int nrows;
    mm* data;

    if (argv[1][0] == 'a') // 'a' to read ascii file
    {
        char* strdata = (char*) malloc(fst.st_size);
        ssize_t read_size = read(fd, strdata, fst.st_size);
        close(fd);
        printf("Read %d bytes of ascii from \"%s\"\n", read_size, argv[2]);

        data = parse_ascii(strdata, &nrows);

        if (argv[1][1] && argv[1][1] == 'c') // 'c' to create binary file
        {
            // TODO check for argc >= 4
            FILE *fp = fopen(argv[4], "w+b");
            fwrite(data, sizeof(mm), nrows, fp);
            fclose(fp);
        }
    }
    else if (argv[1][0] == 'b') // 'b' to read binary file
    {
        // TODO nrows
        read(fd, data, fst.st_size);
    }

    // for (int i = 0; i < 40; i++)
    //     printf("%3d %6i %10llu\n", i, data[i].decay_time, data[i].time_stamp);
    // return 0;

    // int n = fst.st_size / sizeof(mm);
    int minx = 0, maxx = 15000, binw = 500, nbins = maxx/binw;
    int counts[nbins];
    for (int i = 0; i < nbins; ++i) counts[i] = 0;

    for (int i = 0; i < nrows; ++i)
    {
        int j = (minx + data[i].decay_time) / binw;
        if (j < nbins)
            counts[j]++;
    }

    // double log_counts[nbins];
    // for (int i = 0; i < nbins; ++i)
    //     log_counts[i] = log((double) counts[i]);

    for (int i = 0, j = binw/2+minx; i < nbins; ++i, j+=binw)
        printf("%6d %d\n", j, counts[i]);

    return 0;
}
