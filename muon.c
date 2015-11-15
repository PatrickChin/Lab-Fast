#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <math.h>
#include <ctype.h>

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

    if (argv[1][0] == 'b') // 'b' to read binary file
    {
        // TODO debug why this isn't reading anything
        ssize_t read_size = read(fd, data, fst.st_size);
        printf("Read %d bytes of binary data from \"%s\"\n", read_size, argv[2]);

        // This is duplicate code, maybe I should write a function for this
        if (read_size != fst.st_size)
        {
            fprintf(stderr, "\nError: Only read %d of the requested %ld.\n", read_size, fst.st_size);
            char abort[2] = { 0, 0 };
            // TODO compare whole string
            while (abort[0] != 'n')
            {
                fprintf(stderr, "Abort? [y/n]: ");
                scanf("%s", abort);
                if (abort[0] == 'y')
                    return 1;
            }
        }

        nrows = read_size / sizeof(mm);
    }
    else if (argv[1][0] == 'a') // 'a' to read ascii file
    {
        // TODO assume ascii is default
        // this will change indicies of argv
        char* strdata = (char*) malloc(fst.st_size);
        ssize_t read_size = read(fd, strdata, fst.st_size);
        printf("Read %d bytes of ascii data from \"%s\"\n", read_size, argv[2]);

        if (read_size != fst.st_size)
        {
            fprintf(stderr, "\nError: Only read %d of the requested %ld.\n", read_size, fst.st_size);
            char abort[2] = { 0, 0 };
            // TODO compare whole string
            while (abort[0] != 'n')
            {
                fprintf(stderr, "Abort? [y/n]: ");
                scanf("%s", abort);
                if (abort[0] == 'y')
                    return 1;
            }
        }

        data = parse_ascii(strdata, &nrows);

        if (argv[1][1] && argv[1][1] == 'c') // 'c' to create binary file
        {
            if (argc < 4) {
                fprintf(stderr, "\nError: Please enter a binary file to write to as the third argument.\n"
                        "    Continuing without writing a binary file.\n\n");
                // TODO ask to continue/abort without writing to file
            } else {
                FILE *fp = fopen(argv[3], "w+b");
                if (!fp) {
                    fprintf(stderr, "Failed to write to \"%s\".\n", argv[3]);
                    // TODO ask to continue/abort without writing to file
                } else {
                    fwrite(data, sizeof(mm), nrows, fp);
                }
                fclose(fp);
            }
        }
    }
    else
    {
        fprintf(stderr, "Please specify whether the datafile is ascii 'a' or "
                "binary 'b' with the first argument of this program.\n");
        return 1;
    }


    printf("nrows: %d\n\n", nrows);

    close(fd);

    // for (int i = 0; i < 40; i++)
    //     printf("%3d %6i %10llu\n", i, data[i].decay_time, data[i].time_stamp);
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
        log_counts[i] = counts[i] > 0 ? log((double) counts[i]) : 0;
    }

    for (int i = 0, j = binw/2+minx; i < nbins; ++i, j+=binw)
        printf("%6d %8f\n", j, log_counts[i]);

    return 0;
}
