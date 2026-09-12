#include "../../src/classic/number_theory.hpp"
#include <cstdio>

int main()
{
    int t;
    scanf("%d", &t);
    Pollard_Rho solver;
    while ( t-- )
    {
        unsigned long long n;
        scanf("%llu", &n);
        auto factors = solver.Factor(n);
        if ( factors.size() == 1 )
            puts("Prime");
        else
            printf("%llu\n", factors.front());
    }
    return 0;
}
