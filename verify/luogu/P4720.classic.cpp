#include "../../src/classic/exlucas.hpp"
#include <cstdio>

Ex_Lucas<1000000> comb;

int main()
{
    unsigned long long n, m;
    int p;
    scanf("%llu%llu%d", &n, &m, &p);
    comb.Init(p);
    printf("%d\n", comb.Choose(n, m));
}
