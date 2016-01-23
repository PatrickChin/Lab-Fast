#include "muon.h"

int main(int argc, char *argv[])
{
    int size;
    mm* data;
    muon_read_file(&data, &size, argv[1], 1);
    muon_write_binary(&data, size, argv[2]);
    free(data);
    return 0;
}
