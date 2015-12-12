#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <math.h>
#include <ctype.h>
#include <string.h>

typedef struct muon_measurement {
    unsigned int decay_time;
    unsigned long long time_stamp;
} mm;

/**
 * The only significant difference between this and the stdlib implementation
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

    return data;
}

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        printf("TODO - useage");
        return -1;
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0)
    {
        printf("Failed to open \"%s\"\n", argv[1]);
        return -1;
    }

    struct stat fst;
    fstat(fd, &fst);

    int nrows;
    mm* data;

    // TODO assume ascii is default
    // this will change indicies of argv
    char* strdata = (char*) malloc(fst.st_size);
    ssize_t read_size = read(fd, strdata, fst.st_size);
    printf("Read %d bytes of ascii data from \"%s\"\n", read_size, argv[1]);

    if (read_size != fst.st_size+1)
    {
        fprintf(stderr, "\nError: Only read %d of the requested %ld.\n", read_size, fst.st_size);
        char *abort;
        size_t len = 0;
        while (1)
        {
            fprintf(stderr, "Abort? [y/n]: ");
            getline(&abort, &len, stdin);
            if (!strcmp(abort, "yes\x0A") || !strcmp(abort, "y\x0A"))
                return 1;
            if (!strcmp(abort, "no\x0A") || !strcmp(abort, "n\x0A"))
                break;
        }
    }

    data = parse_ascii(strdata, &nrows);

    printf("nrows: %d\n\n", nrows);

    close(fd);

    // for (int i = 0; i < 40; i++)
    //    // printf("%3d %6i %10llu\n", i, data[i].decay_time, data[i].time_stamp);
    // return 0;

    int minx = 0, maxx = 15000, binw = 500, nbins = maxx/binw;
    int counts[nbins];
    for (int i = 0; i < nbins; ++i) counts[i] = 0;

    for (int i = 0; i < nrows; ++i)
    {
        int j = (minx + data[i].decay_time) / binw;
        if (j < nbins)
            counts[j]++;
    }

    double log_counts[nbins];
    for (int i = 0; i < nbins; ++i)
    {
        log_counts[i] = log((double) counts[i] + 1);
    }

    for (int i = 0, j = binw/2+minx; i < nbins; ++i, j+=binw)
        printf("%d %f\n", j, log_counts[i]);

    return 0;
}
