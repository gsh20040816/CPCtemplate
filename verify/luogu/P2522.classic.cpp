#include "../../src/classic/coprime_pairs.hpp"
#include <cstdio>

int main()
{
    Coprime_Pairs solver(50000);
    int t;
    scanf("%d", &t);
    while ( t-- )
    {
        int a, b, c, d, k;
        scanf("%d%d%d%d%d", &a, &b, &c, &d, &k);
        printf("%lld\n", solver.Rectangle(a, b, c, d, k));
    }
    return 0;
}
