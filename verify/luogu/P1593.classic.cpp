#include "../../src/classic/divisor_sum.hpp"
#include <cstdio>

int main()
{
    unsigned long long a, b;
    scanf("%llu%llu", &a, &b);
    Pollard_Rho solver;
    printf("%llu\n", Divisor_Sum_Power(a, b, 9901, solver));
    return 0;
}
