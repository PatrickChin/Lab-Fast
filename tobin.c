#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

long long atoll2(char** str)
{
    long long val = 0;

    while (**str && **str != ' ')
        val = val*10 + (*(*str)++ - '0');

    while (**str && **str == ' ')
        (*str)++;

    return val;
}

int main(int argc, char *argv[])
{
    if (argc != 3)
        return 1;

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0)
        return 1;

    struct stat fst;
    fstat(fd, &fst);

    char* strdata = (char*) malloc(fst.st_size+1);
    read(fd, strdata, fst.st_size);
    strdata[fst.st_size] = '\0';
    close(fd);

    printf("Read \"%s\" (%ld bytes)", argv[1],  fst.st_size);

    long nrows = 0;
    for (long i = 0; i < fst.st_size; ++i)
    {
        if (strdata[i] == '\n' || strdata[i] == '\r')
        {
            strdata[i++] = ' ';
            if (strdata[i] == '\n' || strdata[i] == '\r')
                strdata[i] = ' ';
            ++nrows;
        }
    }

    printf(" (%ld rows)\n", nrows);

    char* pos = strdata;
    long long bindata[nrows*2];
    for (int i = 0; i < 2*nrows; i+=2)
    {
        bindata[i] = atoll2(&pos);
        bindata[i+1] = atoll2(&pos);
    }

    printf("Wrote to: \"%s\"\n", argv[2]);

    FILE *fp = fopen(argv[2], "w+b");
    fwrite(bindata, sizeof(bindata[0]), 2*nrows, fp);
    fclose(fp);

    return 0;
}
