#include "../../src/compact/number_theory.hpp"
#include <cstdio>

int main()
{
    int t;
    scanf("%d", &t);
    PollardRho solver;
    while (t--)
    {
        unsigned long long n;
        scanf("%llu", &n);
        auto factors = solver.factor(n);
        if (factors.size() == 1)
            puts("Prime");
        else
            printf("%llu\n", factors.back());
    }
    return 0;
}
