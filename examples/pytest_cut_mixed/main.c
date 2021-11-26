#include "mixed.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    if(argc != 2) {
        fprintf(stderr, "Wrong number of arguments, one expected!\n");
        return 2;
    }
    // YES atoi is not nice - but meh
    int x = atoi(argv[1]);

    printf("Square: %d\n", square(x));
    printf("Cube: %d\n", cube(x));

    return 0;
}