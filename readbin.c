#include "muon.h"

int main(int argc, char *argv[])
{
    mm* data;
    int size;
    muon_read_file(&data, &size, argv[1], 0);
    printf("size: %d\n", size);
    for (int i = 0; i < size; i++)
        printf("%d %d\n", data[i].decay_time, data[i].time_stamp);

    return 0;
}
