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
    *nrows = 0;
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

    if (argc < 6)
    {
        printf("TODO - useage\n");
        printf("muon infile tmin tmax nbins bg_t_start\n");
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

    int minx = atoi(argv[2]),
        maxx = atoi(argv[3]),
        nbins = atoi(argv[4]),

        timescale = maxx-minx,
        binw = timescale/nbins,

        bgx = atoi(argv[5]),
        bgbin = bgx*nbins/timescale,

        counts = 0,
        counts4k = 0;

    int y[nbins];
    for (int i = 0; i < nbins; ++i) y[i] = 0;

    for (int i = 0; i < nrows; ++i)
    {
        if (data[i].decay_time >= 40000)
            counts4k++;
        else {
            int d = data[i].decay_time - minx;
            if (d < 0) continue; // ignore counts less than minx
            y[d / binw]++, counts++;
        }
    }

    int bgy[counts4k];
    double avgbg = 0, stdevbg = 0;
    for (int i = 0, j = 0; i < nrows; ++i)
        if (data[i].decay_time >= 40000)
        {
            bgy[j] = data[i].decay_time - 40000;
            avgbg += bgy[j];
            stdevbg += bgy[j] * bgy[j];
            j++;
        }
    avgbg /= counts4k;
    stdevbg = sqrt(stdevbg/counts4k - avgbg*avgbg);

    printf("bg counts/second: %.8f (%.8f)\n", avgbg, stdevbg);

    double ynorm[nbins];
    for (int i = 0; i < nbins; ++i)
        ynorm[i] = ((double) y[i]) / binw;

    // for (int i = 0; i < nbins; ++i)
    //     printf("%5f ", ynorm[i]);
    // printf("\n");

    // double logy[nbins];
    // for (int i = 0; i < nbins; ++i)
    //     logy[i] = log((double) y[i] + 1);

    printf("minx %d\nbinw %d\nbins %d\ncounts %d\n", minx, binw, nbins, counts);

    double wxx = 0, wx = 0, wc = 0, wxc = 0, kx2 = 0, sigw = 0, bg = 0,
          bgbins = 0, deta, sigma, B = 0, K = 22000;

    for (int itt = 0; itt < 3; ++itt) // number of time to do the linear regression
    {
        if (timescale > bgx)
        {
            for (int i = bgbin; i < nbins; ++i)
            {
                double x = (i+0.5) * timescale / nbins + minx;
                bgbins++, bg += ynorm[i] - B*exp(-x/K);
            }
            if (bgbins > 0) bg /= bgbins;
        }

        for (int i = 0; i < bgbin && i < nbins; ++i)
        {
            double w = ynorm[i] - bg;
            if (w > 0)
            {
                double C = log(w);
                double x = (i+0.5) * timescale / nbins + minx;
                wxx += w*x*x;
                wx += w*x;
                wc += w*C;
                wxc += w*x*C;
                sigw += w;
            }
        }

        deta = sigw*wxx - wx*wx;
        B = exp((wc*wxx - wx*wxc) / deta);  // background distribution
        K = - deta / (sigw*wxc - wx*wc);    // decay constant i.e. muon lifetime
        sigma = K*K*sqrt(sigw/deta); 

        for (int i = 0; i < nbins; ++i)
        {
           double w = ynorm[i]-bg;
           if (w > 1)
           {
               int x = (i+0.5)*timescale / nbins + minx;
               double fx = B*exp(-x/K);
               // kx2 += (w-fx)*(w-fx) / fx;
               kx2 += w*w/fx + fx - 2*w;
           }
        }
    }

    printf("bg = %.8f\nt = %.8f\nsigma = %.8f\nkx2 = %.8f\n\n", B, K, sigma, kx2 / (nbins-2));

    return 0;
}

