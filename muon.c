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
    }

    return data;
}

int request_abort()
{
    char *abort;
    size_t len = 0;
    while (1)
    {
        printf("Abort? [y/n]: ");
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

    if (argc != 6)
    {
        printf("muon inputfile tmin tmax nbins bg_t_start\n");
        return -1;
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0)
    {
        printf("Failed to open \"%s\"\n", argv[1]);
        return -1;
    }

    // get the file size
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
        printf("\nError: Only read %d of the requested %ld.\n", read_size, fst.st_size);
        if (request_abort())
            return 1;
    }

    data = parse_ascii(strdata, &nrows);
    printf("Parsed %d rows of data.\n\n", nrows);

    int minx = atoi(argv[2]),
        maxx = atoi(argv[3]),
        nbins = atoi(argv[4]),

        timescale = maxx-minx,

        // the minimum time value we assume to be solely background counts
        // this is rounded down to the nearest bin end
        bgx = atoi(argv[5]),

        // the bin `bgx` is in
        bgbin = bgx*nbins/timescale,

        counts = 0, // number of muon events
        counts4k = 0, // number of 40000+ datapoints
        totalt = data[nrows-1].time_stamp - data[0].time_stamp;
    double binw = timescale/nbins;

    printf("minx = %d\n"
           "binw %f\n"
           "bins %d\n", minx, binw, nbins);

    int y[nbins]; // counts in each bin
    for (int i = 0; i < nbins; ++i) y[i] = 0; // initalize each y[i] to zero

    int max4k = 0;
    for (int i = 0; i < nrows; ++i)
    {
        if (data[i].decay_time >= 40000)
        {
            counts4k++;

            // find max n above 40000
            max4k = data[i].decay_time > max4k ? data[i].decay_time : max4k;

        } else {
            if (data[i].decay_time >= maxx) continue; // ignore values bigger than maxx
            if (data[i].decay_time <= minx) continue; // ignore values bigger than minx
            y[(int) ((data[i].decay_time - minx) / binw)]++; // increment the bin that data[i] is to be placed in
            counts++;
        }
    }


    // Not sure if this works so commented it out

    // int bgy[max4k]; // discrete background bin counts
    // double avgbg = 0, stdevbg = 0;
    // for (int i = 0, j = 0; i < nrows; ++i)
    //     if (data[i].decay_time >= 40000)
    //     {
    //         bgy[data[i].decay_time - 40000]++;
    //         stdevbg += bgy[j] * bgy[j];
    //         j++;
    //     }
    // printf("bg counts: %.8f\n", counts4k);
    // avgbg = counts4k / max4k;
    // stdevbg = sqrt(stdevbg/counts4k - avgbg*avgbg);
    // printf("bg counts/second: %.8f (%.8f)\n", avgbg, stdevbg);

    printf("total seconds: %d\n", totalt);

    // dividing each bin count by the binwidth so histograms with different bin
    // widths can be compared
    double ynorm[nbins], dynorm[nbins];
    for (int i = 0; i < nbins; ++i)
    {
        ynorm[i] = ((double) y[i]) / binw;
        dynorm[i] = sqrt(y[i]) / binw;
    }

    fprintf(stderr, "t count dcount\n");
    for (int i = 0; i < nbins; ++i)
        fprintf(stderr, "%.2f %d %.8f\n", (0.5*binw + i*binw), y[i], sqrt(y[i]));
        // fprintf(stderr, "%.2f %.8f %.8f\n", (0.5*binw + i*binw), ynorm[i], dynorm[i]);

    // double logy[nbins];
    // for (int i = 0; i < nbins; ++i)
    //     logy[i] = log((double) y[i] + 1);

    printf("counts %d\n", counts);

    double wxx = 0, wx = 0, wc = 0, wxc = 0, kx2 = 0, sigw = 0, y0 = 0,
          bgbins = 0, deta, sigma, A0 = 0, tau = 22000;

    for (int itt = 0; itt < 3; ++itt) // number of time to remove background counts
    {

        if (timescale > bgx)
        {
            for (int i = bgbin; i < nbins; ++i)
            {
                double x = (i+0.5) * timescale / nbins + minx;
                bgbins++;
                y0 += ynorm[i] - A0*exp(-x/tau);
            }
            if (bgbins > 0)
                y0 /= bgbins;
        }

        for (int i = 0; i < bgbin && i < nbins; ++i)
        {
            double w = ynorm[i] - y0;
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

        deta = sigw*wxx - wx*wx; // temp variable
        A0 = exp((wc*wxx - wx*wxc) / deta); // background distribution
        tau = - deta / (sigw*wxc - wx*wc); // decay constant i.e. muon lifetime
        sigma = tau*tau*sqrt(sigw/deta); 

        for (int i = 0; i < nbins; ++i)
        {
           double w = ynorm[i]-y0;
           if (w > 1)
           {
               int x = (i+0.5)*timescale / nbins + minx;
               double fx = A0*exp(-x/tau);
               // kx2 += (w-fx)*(w-fx) / fx;
               kx2 += w*w/fx + fx - 2*w;
           }
        }
    }

    printf("A0 = %.8f\n"
           "tau = %.8f\n"
           "y0 = %.8f\n"
           "sigma = %.8f\n"
           "kx2 = %.8f\n"
           "\n",
           A0, tau, y0, sigma, kx2 / (nbins-2));

    return 0;
}

