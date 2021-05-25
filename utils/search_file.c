#define likely(x)       __builtin_expect(!!(x), 1)
#define unlikely(x)     __builtin_expect(!!(x), 0)

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    long i;
    char *core_file;
    long address;
    unsigned char u8[8];
    FILE *fp = NULL;
    unsigned char *data  = NULL;

    if (argc != 3) {
      printf("usage: %s core addr\n", argv[0]);
      return 1;
    }

    core_file = argv[1];
    address = strtol(argv[2], NULL, 16);
    memcpy(u8, &address, sizeof(address));
    printf("search 0x%lx\n", address);

    fp = fopen(core_file, "rb");
    if (fp == NULL) {
        printf("can not open %s\n", core_file);
        goto failed;
    }

    if (fseek(fp, 0, SEEK_END) != 0) {
        printf("seek to end failed\n");
        goto failed;
    }

    long size = ftell(fp);
    if (fseek(fp, 0, SEEK_SET) != 0) {
        printf("seek to start failed\n");
        goto failed;
    }

    data = malloc(size);
    if (data == NULL) {
        printf("can not alloc for size %ld\n", size);
        goto failed;
    }

    if (fread(data, size, 1, fp) != 1) {
        printf("failed to read from file\n");
        goto failed;
    }

    fclose(fp);
    fp = NULL;

    for (i = 0; i < size - 8; i++) {
        if (unlikely(data[i] != u8[0])) {
            continue;
        }

        if (data[i + 1] == u8[1]
            && data[i + 2] == u8[2]
            && data[i + 3] == u8[3]
            && data[i + 4] == u8[4]
            && data[i + 5] == u8[5]
            && data[i + 6] == u8[6]
            && data[i + 7] == u8[7]) {
            printf("offset 0x%016lx\n", i);
            i = i + 8;
        }
    }

    free(data);

    return 0;

failed:

    if (data) {
        free(data);
    }

    if (fp) {
        fclose(fp);
    }

    return 1;
}
