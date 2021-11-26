#define CUT_MAIN
#include "cut.h"
#include "mixed.h"

TEST(square) {
    SUBTEST(one) {
        ASSERT(square(1) == 1);
    }

    SUBTEST(positive) {
        ASSERT(square(2) == 4);
        ASSERT(square(3) == 9);
    }

    SUBTEST(negative) {
        ASSERT(square(-2) == 4);
        ASSERT(square(-3) == 9);
    }
}


TEST(cube) {
    SUBTEST(one) {
        ASSERT(cube(1) == 1);
    }

    SUBTEST(positive) {
        ASSERT(cube(2) == 8);
        ASSERT(cube(3) == 27);
    }

    SUBTEST(negative) {
        ASSERT(cube(-2) == -8);
        ASSERT(cube(-3) == -27);
    }
}