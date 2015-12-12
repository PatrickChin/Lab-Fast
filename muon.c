#define _GNU_SOURCE
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

int request_abort()
{
    char *abort;
    size_t len = 0;
    while (1)
    {
        fprintf(stderr, "Abort? [y/n]: ");
        getline(&abort, &len, stdin);
        // "\x0A" is the new line feed from getline
        if (!strcmp(abort, "yes\x0A") || !strcmp(abort, "y\x0A"))
            return 1;
        if (!strcmp(abort, "no\x0A") || !strcmp(abort, "n\x0A"))
            return 0;
    }
}

int main(int argc, char *argv[])
{
    if (argc < 5)
    {
        printf("TODO - useage\n");
        printf("muon infile minx maxx nbins\n");
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
    close(fd);
    printf("Read %d bytes of ascii data from \"%s\".\n", read_size, argv[1]);

    if (read_size != fst.st_size)
    {
        fprintf(stderr, "\nError: Only read %d of the requested %ld.\n", read_size, fst.st_size);
        if (request_abort())
            return 1;
    }

    data = parse_ascii(strdata, &nrows);
    printf("Parsed %d rows of data.\n\n", nrows);


    // for (int i = 0; i < 40; i++)
    //    // printf("%3d %6i %10llu\n", i, data[i].decay_time, data[i].time_stamp);
    // return 0;

    int minx = atoi(argv[2]),
        maxx = atoi(argv[3]),
        nbins = atoi(argv[4]),
        timescale = maxx-minx,
        binw = timescale/nbins,
        counts = 0,
        y[nbins];
    for (int i = 0; i < nbins; ++i) y[i] = 0;

    for (int i = 0; i < nrows; ++i)
    {
        int j = (minx + data[i].decay_time) / binw;
        if (j < nbins)
            y[j]++, counts++;
    }

    double logy[nbins];
    for (int i = 0; i < nbins; ++i)
        logy[i] = log((double) y[i] + 1);

    printf("minx %d\nbinw %d\nbins %d\ncounts %d\n", minx, binw, nbins, counts);

    for (int i = 0; i < nbins; ++i)
        printf("%4d   ", i);
    printf("\n");

    for (int i = 0; i < nbins; ++i)
        printf("%4d   ", y[i]);
    printf("\n");

    for (int i = 0; i < nbins; ++i)
        printf("%1.2f   ", logy[i]);
    printf("\n");

    float wxx = 0, wx = 0, wc = 0, wxc = 0, kx2 = 0, sigw = 0, bg = 0;

    for (int i = 0; i < nbins; ++i)
    {
        float w = y[i] - bg;
        if (w > 0)
        {
            float C = log(w);
            float x = (i+0.5) * timescale / nbins;
            wxx += w*x*x;
            wx += w*x;
            wc += w*C;
            wxc += w*x*C;
            sigw += w;
        }
    }

    float deta = sigw*wxx - wx*wx;
    float B = exp((wc*wxx - wx*wxc) / deta);
    float K = - deta / (sigw*wxc - wx*wc);

    float sigma = K*K*sqrt(sigw/deta); 

    for (int i = 0; i < nbins; ++i)
    {
       float w = y[i]-bg;
       if (w > 1)
       {
           int x = (i+0.5)*timescale / nbins;
           kx2 += (w - B*exp(-x/K)) * (w - B*exp(-x/K)) / w;
       }
    }

    printf("B = %f\nK = %f\nsigma = %f\n", B, K, sigma);

    return 0;
}
