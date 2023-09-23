#include <stdio.h>
#include <unistd.h>

extern void foo_b();

int main(int argc, char *argv[]) {
    printf("ccc\n");

    foo_b();

    return 0;
}