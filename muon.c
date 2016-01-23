#include "muon.h"

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

/**
 * The `str` argument must be NUL terminated
 * nrows are calculated by 1 + the number of `\n` characters
 */
void muon_parse_str(char* str, mm** data, int* nrows)
{
    *nrows = 0;
    char* pos = str;
    while (*pos)
        if (*pos++ == '\n')
            (*nrows)++;
    pos = str;

    (*data) = (mm*) malloc((*nrows)*sizeof(mm));
    for (int i = 0; i < *nrows; ++i)
    {
        (*data)[i].decay_time = atoll2(&pos);
        (*data)[i].time_stamp = atoll2(&pos);
    }
}

ssize_t muon_read_file(mm** data, int* nrows, char* f, int ascii)
{
    FILE* fp = fopen(f, "rb");
    struct stat fst;
    fstat(fileno(fp), &fst);

    ssize_t read_size = 0;

    if (ascii)
    {
        char* strdata = (char*) malloc(fst.st_size);
        read_size = fread(strdata, 1, fst.st_size, fp);
        fclose(fp);

        muon_parse_str(strdata, data, nrows);
    }
    else
    {
        *nrows = fst.st_size / sizeof(mm);
        *data = (mm*) malloc(fst.st_size);
        read_size = fread(*data, 1, fst.st_size, fp);
        fclose(fp);
    }

    if (read_size == 0 || read_size != fst.st_size)
        printf("\nError: Read %d of the requested %ld.\n"
               "Continuing anyway ...\n", read_size, fst.st_size);

    return read_size;
}

ssize_t muon_write_binary(mm** data, int size, char* file)
{
    FILE* fp = fopen(file, "wb");
    size_t r = fwrite((*data), sizeof(mm), size, fp);
    fclose(fp);
    return r;
}

