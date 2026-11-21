#ifndef TEST_H
#define TEST_H

#include <stdio.h>

static int test_basarisiz = 0;
static int test_sayac = 0;

#define KONTROL(kosul)                                                              \
    do {                                                                            \
        test_sayac++;                                                               \
        if (!(kosul)) {                                                             \
            test_basarisiz++;                                                       \
            printf("BASARISIZ %s:%d: %s\n", __FILE__, __LINE__, #kosul);            \
        }                                                                           \
    } while (0)

#define SONUC(ad)                                                                   \
    do {                                                                            \
        printf("%s: %d kontrol, %d basarisiz\n", ad, test_sayac, test_basarisiz);   \
        return test_basarisiz ? 1 : 0;                                              \
    } while (0)

#endif
