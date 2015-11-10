#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

int main(int argc, char *argv[])
{
    if (argc < 1)
        return 1;

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0)
        return 1;

    struct stat fst;
    fstat(fd, &fst);

    long long* data = (long long*) malloc(fst.st_size);
    read(fd, data, fst.st_size);
    close(fd);

    int n = fst.st_size / sizeof(long long);

    int minx = 0, maxx = 15000, binw = 500, nbins = maxx/binw;

    int counts[nbins];
    for (int i = 0; i < nbins; ++i) counts[i] = 0;

    for (int i = 0; i < n; i+=2)
    {
        int j = (minx + (int) data[i]) / binw;
        if (j < nbins)
            counts[j]++;
    }

    // double log_counts[nbins];
    // for (int i = 0; i < nbins; ++i)
    //     log_counts[i] = log((double) counts[i]);

    for (int i = 0, j = binw/2+minx; i < nbins; ++i, j+=binw)
        printf("%d %d\n", j, counts[i]);

    return 0;
}
