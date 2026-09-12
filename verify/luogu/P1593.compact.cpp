#include "../../src/compact/divisor_sum.hpp"
#include <cstdio>

int main()
{
    unsigned long long a, b;
    scanf("%llu%llu", &a, &b);
    PollardRho solver;
    printf("%llu\n", divisor_sum_power(a, b, 9901, solver));
    return 0;
}
